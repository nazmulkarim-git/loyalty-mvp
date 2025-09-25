from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from .database import get_db, engine, Base
from . import models
from .schemas import OTPRequest, OTPVerify, Token, SetPIN
from .auth_utils import create_access_token
from .config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

Base.metadata.create_all(bind=engine)

def normalize_phone(p: str) -> str:
    return p.strip().replace(" ", "")

@router.post("/request-otp")
def request_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    phone = normalize_phone(payload.phone)
    code = f"{random.randint(0, 999999):06d}"
    otp = models.OTPCode(phone_e164=phone, code=code, expires_at=datetime.utcnow() + timedelta(minutes=10))
    db.add(otp); db.commit()
    user = db.query(models.User).filter(models.User.phone_e164 == phone).first()
    if not user:
        user = models.User(phone_e164=phone, name=payload.name or "User", email=payload.email, dob=payload.dob)
        if settings.ADMIN_PHONE and phone == settings.ADMIN_PHONE:
            user.role = models.RoleEnum.ADMIN
        db.add(user); db.commit()
    else:
        if payload.name: user.name = payload.name
        if payload.email: user.email = payload.email
        if payload.dob: user.dob = payload.dob
        db.commit()
    resp = {"ok": True, "message": "OTP sent (development mode returns it)."}
    if settings.DEV_RETURN_OTP_IN_RESPONSE:
        resp["dev_otp"] = code
    print(f"[DEV] OTP for {phone}: {code}")
    return resp

@router.post("/verify-otp", response_model=Token)
def verify_otp(payload: OTPVerify, db: Session = Depends(get_db)):
    phone = normalize_phone(payload.phone)
    otp = db.query(models.OTPCode).filter(models.OTPCode.phone_e164==phone).order_by(models.OTPCode.created_at.desc()).first()
    if not otp or otp.code != payload.code or otp.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    user = db.query(models.User).filter(models.User.phone_e164 == phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found after OTP")
    access_token = create_access_token({"sub": user.id, "role": user.role})
    return Token(access_token=access_token, role=user.role)

@router.post("/set-pin")
def set_pin(payload: SetPIN, db: Session = Depends(get_db)):
    return {"ok": True, "message": "PIN flow stubbed in MVP."}
