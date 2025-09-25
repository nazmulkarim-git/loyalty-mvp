from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from . import models
from .routers_auth import router as auth_router
from .routers_users import router as users_router
from .routers_merchants import router as merchants_router
from .routers_enrollments import router as enrollments_router
from .routers_stamps import router as stamps_router
from .routers_redemptions import router as redeem_router
from .routers_admin import router as admin_router
from .auth_utils import hash_pin
from .config import settings
import os

Base.metadata.create_all(bind=engine)

def seed_if_empty():
    db: Session = SessionLocal()
    try:
        # Seed admin with pin
        if settings.ADMIN_PHONE and settings.ADMIN_PIN:
            admin = db.query(models.User).filter(models.User.phone_e164==settings.ADMIN_PHONE).first()
            if not admin:
                admin = models.User(phone_e164=settings.ADMIN_PHONE, name="Anni Admin", role=models.RoleEnum.ADMIN, pin_hash=hash_pin(settings.ADMIN_PIN))
                db.add(admin); db.commit()
            elif not admin.pin_hash:
                admin.pin_hash = hash_pin(settings.ADMIN_PIN); db.commit()

        any_merchant = db.query(models.Merchant).first()
        if not any_merchant:
            owner = db.query(models.User).filter(models.User.role==models.RoleEnum.ADMIN).first()
            if not owner:
                owner = models.User(phone_e164="+8801000000000", name="Admin", role=models.RoleEnum.ADMIN, pin_hash=hash_pin("1234"))
                db.add(owner); db.commit(); db.refresh(owner)
            demo = models.Merchant(owner_user_id=owner.id, business_name="Sample Café", business_type="Cafe", location_text="Gulshan, Dhaka", stamps_required=9, is_active=True)
            db.add(demo); db.commit()
            print("[SEED] Created Sample Café so the list isn't empty.")
    finally:
        db.close()

seed_if_empty()

app = FastAPI(title="AnniCard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # same-origin in prod; wildcard fine for MVP (no auth headers besides cookie)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(merchants_router)
app.include_router(enrollments_router)
app.include_router(stamps_router)
app.include_router(redeem_router)
app.include_router(admin_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
