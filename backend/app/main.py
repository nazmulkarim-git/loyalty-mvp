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
from .routers_reports import router as reports_router
from .routers_admin import router as admin_router
from .config import settings
import os

Base.metadata.create_all(bind=engine)

def seed_if_empty():
    db: Session = SessionLocal()
    try:
        any_merchant = db.query(models.Merchant).first()
        if not any_merchant:
            if settings.ADMIN_PHONE:
                admin = db.query(models.User).filter(models.User.phone_e164==settings.ADMIN_PHONE).first()
                if not admin:
                    admin = models.User(phone_e164=settings.ADMIN_PHONE, name="Admin", role=models.RoleEnum.ADMIN)
                    db.add(admin); db.commit(); db.refresh(admin)
            else:
                admin = models.User(phone_e164="+8801000000000", name="Admin", role=models.RoleEnum.ADMIN)
                db.add(admin); db.commit(); db.refresh(admin)
            demo = models.Merchant(owner_user_id=admin.id, cafe_name="Sample Café", location_text="Gulshan, Dhaka", stamps_required=9, is_active=True)
            db.add(demo); db.commit()
            print("[SEED] Created Sample Café so the list isn't empty.")
    finally:
        db.close()

seed_if_empty()

app = FastAPI(title="Loyalty MVP API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
app.include_router(reports_router)
app.include_router(admin_router)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
