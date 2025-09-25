from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .schemas import MerchantOut, RedemptionOut
from .auth_utils import require_role

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/merchants", response_model=list[MerchantOut])
def all_merchants(admin=Depends(require_role(models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    rows = db.query(models.Merchant).all()
    return [MerchantOut(id=m.id, cafe_name=m.cafe_name, logo_url=m.logo_url, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active) for m in rows]

@router.patch("/merchants/{merchant_id}/stamps", response_model=MerchantOut)
def set_stamps_required(merchant_id: str, stamps_required: int, admin=Depends(require_role(models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    m = db.query(models.Merchant).filter(models.Merchant.id == merchant_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found")
    m.stamps_required = stamps_required
    db.commit()
    return MerchantOut(id=m.id, cafe_name=m.cafe_name, logo_url=m.logo_url, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active)

@router.patch("/merchants/{merchant_id}/toggle", response_model=MerchantOut)
def toggle_active(merchant_id: str, active: bool, admin=Depends(require_role(models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    m = db.query(models.Merchant).filter(models.Merchant.id == merchant_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found")
    m.is_active = active
    db.commit()
    return MerchantOut(id=m.id, cafe_name=m.cafe_name, logo_url=m.logo_url, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active)

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
        result.append(RedemptionOut(id=r.id, status=r.status, merchant_id=m.id, merchant_name=m.cafe_name, requested_at=r.created_at))
    return result
