from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models
from ..schemas import MerchantCreate, MerchantOut
from ..auth_utils import get_current_user, require_role
from ..config import settings

router = APIRouter(prefix="/merchants", tags=["merchants"])

@router.get("", response_model=list[MerchantOut])
def list_merchants(db: Session = Depends(get_db)):
    merchants = db.query(models.Merchant).filter(models.Merchant.is_active==True).all()
    return [MerchantOut(id=m.id, cafe_name=m.cafe_name, logo_url=m.logo_url, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active) for m in merchants]

@router.post("/register", response_model=MerchantOut)
def register_merchant(payload: MerchantCreate, db: Session = Depends(get_db), current=Depends(get_current_user)):
    if settings.MERCHANT_SIGNUP_CODE and payload.signup_code != settings.MERCHANT_SIGNUP_CODE and current.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Invalid signup code")
    # upgrade user role to merchant if not admin
    if current.role != models.RoleEnum.ADMIN:
        current.role = models.RoleEnum.MERCHANT
    m = models.Merchant(owner_user_id=current.id, cafe_name=payload.cafe_name, logo_url=payload.logo_url, location_text=payload.location_text,
                        stamps_required=payload.stamps_required, is_active=True)
    db.add(m)
    db.commit()
    db.refresh(m)
    return MerchantOut(id=m.id, cafe_name=m.cafe_name, logo_url=m.logo_url, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active)

@router.patch("/{merchant_id}/settings", response_model=MerchantOut)
def update_settings(merchant_id: str, stamps_required: int, db: Session = Depends(get_db), admin=Depends(require_role(models.RoleEnum.ADMIN))):
    m = db.query(models.Merchant).filter(models.Merchant.id==merchant_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found")
    m.stamps_required = stamps_required
    db.commit()
    return MerchantOut(id=m.id, cafe_name=m.cafe_name, logo_url=m.logo_url, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active)
