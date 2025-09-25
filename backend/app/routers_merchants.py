from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .schemas import MerchantOut
from .auth_utils import get_current_user

router = APIRouter(prefix="/merchants", tags=["merchants"])

@router.get("", response_model=list[MerchantOut])
def list_merchants(db: Session = Depends(get_db)):
    merchants = db.query(models.Merchant).filter(models.Merchant.is_active==True).all()
    return [MerchantOut(id=m.id, business_name=m.business_name, business_type=m.business_type, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active) for m in merchants]

@router.get("/mine", response_model=MerchantOut | None)
def my_merchant(current=Depends(get_current_user), db: Session = Depends(get_db)):
    m = db.query(models.Merchant).filter(models.Merchant.owner_user_id==current.id).first()
    if not m:
        return None
    return MerchantOut(id=m.id, business_name=m.business_name, business_type=m.business_type, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active)
