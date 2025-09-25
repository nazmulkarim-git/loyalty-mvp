from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from ..database import get_db, engine, Base
from .. import models
from ..schemas import OTPRequest, OTPVerify, Token, SetPIN, UserOut
from ..auth_utils import create_access_token, hash_pin
from ..config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

# Ensure tables exist on first import (simple MVP)
Base.metadata.create_all(bind=engine)

def normalize_phone(p: str) -> str:
    return p.strip().replace(" ", "")

@router.post("/request-otp")
def request_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    phone = normalize_phone(payload.phone)
    code = f"{random.randint(0, 999999):06d}"
    # store OTP
    otp = models.OTPCode(phone_e164=phone, code=code, expires_at=datetime.utcnow() + timedelta(minutes=10))
    db.add(otp)
    db.commit()
    # Upsert user metadata (without creating full account until verify)
    user = db.query(models.User).filter(models.User.phone_e164 == phone).first()
    if not user:
        user = models.User(phone_e164=phone, name=payload.name or "User", email=payload.email, dob=payload.dob)
        # auto-admin if phone matches
        if settings.ADMIN_PHONE and phone == settings.ADMIN_PHONE:
            user.role = models.RoleEnum.ADMIN
        db.add(user)
        db.commit()
    else:
        if payload.name: user.name = payload.name
        if payload.email: user.email = payload.email
        if payload.dob: user.dob = payload.dob
        db.commit()
    resp = {"ok": True, "message": "OTP sent (development mode prints/returns it)."}
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
        raise HTTPException(status_code=404, detail="User not found after OTP (unexpected)")
    access_token = create_access_token({"sub": user.id, "role": user.role})
    return Token(access_token=access_token, role=user.role)

@router.post("/set-pin")
def set_pin(payload: SetPIN, db: Session = Depends(get_db),):
    # For MVP, this is a no-auth endpoint that updates the latest verified phone.
    # In production you'd bind to current user; here we'll skip PIN-flow in FE.
    return {"ok": True, "message": "PIN flow is stubbed in MVP; store client-side for quick unlock."}

@router.get("/me", response_model=UserOut)
def me(user: models.User = Depends(lambda db=Depends(get_db): db.query(models.User).first())):
    # This stubbed endpoint isn't used; real /me below in users router.
    raise HTTPException(status_code=404, detail="Use /users/me")
