from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from . import models
from .routers_auth import router as auth_router
from .routers_users import router as users_router
from .routers_merchants import router as merchants_router
from .routers_enrollments import router as enrollments_router
from .routers_stamps import router as stamps_router
from .routers_redemptions import router as redeem_router
from .routers_reports import router as reports_router
import os

Base.metadata.create_all(bind=engine)

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

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
