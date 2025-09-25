from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .schemas import StampAdd
from .auth_utils import require_role

router = APIRouter(prefix="/stamps", tags=["stamps"])

@router.post("/add")
def add_stamp(payload: StampAdd, db: Session = Depends(get_db), merchant=Depends(require_role(models.RoleEnum.MERCHANT, models.RoleEnum.ADMIN))):
    m = db.query(models.Merchant).filter(models.Merchant.id==payload.merchant_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Merchant not found")
    user = db.query(models.User).filter(models.User.phone_e164==payload.customer_phone).first()
    if not user:
        user = models.User(phone_e164=payload.customer_phone, name="Customer")
        db.add(user); db.commit(); db.refresh(user)
    e = db.query(models.Enrollment).filter(models.Enrollment.user_id==user.id, models.Enrollment.merchant_id==m.id).first()
    if not e:
        e = models.Enrollment(user_id=user.id, merchant_id=m.id, stamps_count=0, total_stamps=0)
        db.add(e); db.commit(); db.refresh(e)
    db.add(models.Stamp(enrollment_id=e.id, merchant_user_id=merchant.id))
    e.stamps_count = min(e.stamps_count + 1, m.stamps_required)
    e.total_stamps += 1
    db.commit()
    eligible = (e.stamps_count >= m.stamps_required)
    return {"ok": True, "stamps_count": e.stamps_count, "stamps_required": m.stamps_required, "eligible_for_redeem": eligible}
