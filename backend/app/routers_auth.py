from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from .database import get_db, engine, Base
from . import models
from .schemas import (
    CustomerSignupIn, CustomerSigninIn, UserOut, CustomerProfileUpdateIn,
    MerchantSignupIn, MerchantSigninIn
)
from .auth_utils import create_access_token, set_session_cookie, clear_session_cookie, get_current_user, hash_pin, verify_pin
from .config import settings
from datetime import timedelta

router = APIRouter(prefix="/auth", tags=["auth"])

Base.metadata.create_all(bind=engine)

def normalize_phone(p: str) -> str:
    return p.strip().replace(" ", "")

@router.get("/session", response_model=UserOut)
def session_me(user: models.User = Depends(get_current_user)):
    return UserOut(id=user.id, phone_e164=user.phone_e164, name=user.name, email=user.email, dob=user.dob, role=user.role)

@router.post("/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {"ok": True}

# Customer
@router.post("/customer/signup")
def customer_signup(payload: CustomerSignupIn, response: Response, db: Session = Depends(get_db)):
    if payload.pin != payload.confirm_pin:
        raise HTTPException(status_code=400, detail="Pins do not match")
    phone = normalize_phone(payload.phone)
    exists = db.query(models.User).filter(models.User.phone_e164 == phone).first()
    if exists:
        raise HTTPException(status_code=400, detail="Phone already registered")
    u = models.User(phone_e164=phone, name=payload.name, dob=payload.dob, role=models.RoleEnum.CUSTOMER, pin_hash=hash_pin(payload.pin))
    db.add(u); db.commit(); db.refresh(u)
    token, max_age = create_access_token({"sub": u.id, "role": u.role}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    set_session_cookie(response, token, max_age)
    return {"ok": True}

@router.post("/customer/signin")
def customer_signin(payload: CustomerSigninIn, response: Response, db: Session = Depends(get_db)):
    phone = normalize_phone(payload.phone)
    u = db.query(models.User).filter(models.User.phone_e164==phone).first()
    if not u or not u.pin_hash or not verify_pin(payload.pin, u.pin_hash):
        raise HTTPException(status_code=400, detail="Invalid phone or pin")
    if u.role != models.RoleEnum.CUSTOMER:
        raise HTTPException(status_code=403, detail="Use the correct portal for your role")
    token, max_age = create_access_token({"sub": u.id, "role": u.role}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    set_session_cookie(response, token, max_age)
    return {"ok": True}

@router.patch("/customer/profile", response_model=UserOut)
def customer_update_profile(payload: CustomerProfileUpdateIn, user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role != models.RoleEnum.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can edit their profile")
    if payload.phone:
        user.phone_e164 = normalize_phone(payload.phone)
    if payload.name:
        user.name = payload.name
    if payload.email is not None:
        user.email = payload.email
    if payload.dob is not None:
        user.dob = payload.dob
    if payload.pin or payload.confirm_pin:
        if payload.pin != payload.confirm_pin:
            raise HTTPException(status_code=400, detail="Pins do not match")
        user.pin_hash = hash_pin(payload.pin)
    db.commit(); db.refresh(user)
    return UserOut(id=user.id, phone_e164=user.phone_e164, name=user.name, email=user.email, dob=user.dob, role=user.role)

# Merchant
@router.post("/merchant/signup")
def merchant_signup(payload: MerchantSignupIn, response: Response, db: Session = Depends(get_db)):
    if payload.pin != payload.confirm_pin:
        raise HTTPException(status_code=400, detail="Pins do not match")
    if settings.MERCHANT_SIGNUP_CODE and payload.signup_code != settings.MERCHANT_SIGNUP_CODE:
        raise HTTPException(status_code=403, detail="Invalid signup code")
    phone = normalize_phone(payload.phone)
    exists = db.query(models.User).filter(models.User.phone_e164 == phone).first()
    if exists:
        raise HTTPException(status_code=400, detail="Phone already registered")
    u = models.User(phone_e164=phone, name=payload.owner_name, role=models.RoleEnum.MERCHANT, pin_hash=hash_pin(payload.pin))
    db.add(u); db.commit(); db.refresh(u)
    m = models.Merchant(owner_user_id=u.id, business_name=payload.business_name, business_type=payload.business_type, location_text=payload.location_text, stamps_required=9, is_active=True)
    db.add(m); db.commit()
    token, max_age = create_access_token({"sub": u.id, "role": u.role}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    set_session_cookie(response, token, max_age)
    return {"ok": True}

@router.post("/merchant/signin")
def merchant_signin(payload: MerchantSigninIn, response: Response, db: Session = Depends(get_db)):
    phone = normalize_phone(payload.phone)
    u = db.query(models.User).filter(models.User.phone_e164==phone).first()
    if not u or not u.pin_hash or not verify_pin(payload.pin, u.pin_hash):
        raise HTTPException(status_code=400, detail="Invalid phone or pin")
    if u.role != models.RoleEnum.MERCHANT:
        raise HTTPException(status_code=403, detail="Use the correct portal for your role")
    token, max_age = create_access_token({"sub": u.id, "role": u.role}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    set_session_cookie(response, token, max_age)
    return {"ok": True}

# Admin
@router.post("/admin/signin")
def admin_signin(payload: MerchantSigninIn, response: Response, db: Session = Depends(get_db)):
    phone = normalize_phone(payload.phone)
    u = db.query(models.User).filter(models.User.phone_e164==phone).first()
    if not u:
        raise HTTPException(status_code=400, detail="Invalid admin credentials")
    if u.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not an admin")
    if not u.pin_hash or not verify_pin(payload.pin, u.pin_hash):
        raise HTTPException(status_code=400, detail="Invalid admin credentials")
    token, max_age = create_access_token({"sub": u.id, "role": u.role}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    set_session_cookie(response, token, max_age)
    return {"ok": True}
