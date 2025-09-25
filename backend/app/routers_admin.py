from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .schemas import MerchantOut, UserOut, RedemptionOut
from .auth_utils import require_role, hash_pin
from typing import Optional

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/merchants", response_model=list[MerchantOut])
def all_merchants(admin=Depends(require_role(models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    rows = db.query(models.Merchant).all()
    return [MerchantOut(id=m.id, business_name=m.business_name, business_type=m.business_type, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active) for m in rows]

@router.patch("/merchants/{merchant_id}", response_model=MerchantOut)
def edit_merchant(merchant_id: str, business_name: Optional[str]=None, business_type: Optional[str]=None, location_text: Optional[str]=None, stamps_required: Optional[int]=None, is_active: Optional[bool]=None, admin=Depends(require_role(models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    m = db.query(models.Merchant).filter(models.Merchant.id == merchant_id).first()
    if not m: raise HTTPException(status_code=404, detail="Merchant not found")
    if business_name is not None: m.business_name = business_name
    if business_type is not None: m.business_type = business_type
    if location_text is not None: m.location_text = location_text
    if stamps_required is not None: m.stamps_required = stamps_required
    if is_active is not None: m.is_active = is_active
    db.commit(); db.refresh(m)
    return MerchantOut(id=m.id, business_name=m.business_name, business_type=m.business_type, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active)

@router.get("/users", response_model=list[UserOut])
def all_users(admin=Depends(require_role(models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    rows = db.query(models.User).all()
    return [UserOut(id=u.id, phone_e164=u.phone_e164, name=u.name, email=u.email, dob=u.dob, role=u.role) for u in rows]

@router.patch("/users/{user_id}", response_model=UserOut)
def edit_user(user_id: str, name: Optional[str]=None, email: Optional[str]=None, phone: Optional[str]=None, role: Optional[str]=None, pin: Optional[str]=None, admin=Depends(require_role(models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    u = db.query(models.User).filter(models.User.id==user_id).first()
    if not u: raise HTTPException(status_code=404, detail="User not found")
    if name is not None: u.name = name
    if email is not None: u.email = email
    if phone is not None: u.phone_e164 = phone
    if role is not None: u.role = role
    if pin is not None: u.pin_hash = hash_pin(pin)
    db.commit(); db.refresh(u)
    return UserOut(id=u.id, phone_e164=u.phone_e164, name=u.name, email=u.email, dob=u.dob, role=u.role)

@router.get("/pending", response_model=list[RedemptionOut])
def pending_all(admin=Depends(require_role(models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    rows = (
        db.query(models.Redemption, models.Enrollment, models.Merchant)
          .join(models.Enrollment, models.Redemption.enrollment_id == models.Enrollment.id)
          .join(models.Merchant, models.Enrollment.merchant_id == models.Merchant.id)
          .filter(models.Redemption.status == "requested")
          .all()
    )
    result = []
    for r, e, m in rows:
        result.append(RedemptionOut(id=r.id, status=r.status, merchant_id=m.id, merchant_name=m.business_name, requested_at=r.created_at))
    return result
