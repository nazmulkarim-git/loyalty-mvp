from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .schemas import RedeemRequestIn, RedeemApproveIn, RedemptionOut
from .auth_utils import get_current_user, require_role

router = APIRouter(prefix="/redeem", tags=["redeem"])

@router.post("/request")
def request_redeem(payload: RedeemRequestIn, current=Depends(get_current_user), db: Session = Depends(get_db)):
    e = db.query(models.Enrollment).filter(
        models.Enrollment.user_id == current.id,
        models.Enrollment.merchant_id == payload.merchant_id
    ).first()
    if not e:
        raise HTTPException(status_code=400, detail="No stamps with this merchant yet")
    m = db.query(models.Merchant).filter(models.Merchant.id == payload.merchant_id).first()
    if e.stamps_count < m.stamps_required:
        raise HTTPException(status_code=400, detail="Not enough stamps to redeem")
    r = models.Redemption(enrollment_id=e.id, status="requested", requested_by=current.id)
    db.add(r); db.commit(); db.refresh(r)
    return {"ok": True, "redemption_id": r.id}

@router.get("/pending", response_model=list[RedemptionOut])
def pending_redemptions(merchant=Depends(require_role(models.RoleEnum.MERCHANT, models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    m = db.query(models.Merchant).filter(models.Merchant.owner_user_id == merchant.id).first()
    if not m:
        return []
    rows = (
        db.query(models.Redemption, models.Enrollment, models.Merchant)
          .join(models.Enrollment, models.Redemption.enrollment_id == models.Enrollment.id)
          .join(models.Merchant, models.Enrollment.merchant_id == models.Merchant.id)
          .filter(models.Redemption.status == "requested", models.Enrollment.merchant_id == m.id)
          .all()
    )
    result = []
    for r, e, mm in rows:
        result.append(RedemptionOut(id=r.id, status=r.status, merchant_id=mm.id, merchant_name=mm.business_name, requested_at=r.created_at))
    return result

@router.post("/approve")
def approve_redemption(payload: RedeemApproveIn, merchant=Depends(require_role(models.RoleEnum.MERCHANT, models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    r = db.query(models.Redemption).filter(models.Redemption.id == payload.redemption_id).first()
    if not r or r.status != "requested":
        raise HTTPException(status_code=404, detail="Redemption not found or already handled")
    e = db.query(models.Enrollment).filter(models.Enrollment.id == r.enrollment_id).first()
    m = db.query(models.Merchant).filter(models.Merchant.id == e.merchant_id).first()
    own = db.query(models.Merchant).filter(models.Merchant.owner_user_id == merchant.id, models.Merchant.id == m.id).first()
    if not own and merchant.role != models.RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to approve this redemption")
    e.stamps_count = 0
    r.status = "approved"
    r.approved_by = merchant.id
    from datetime import datetime
    r.approved_at = datetime.utcnow()
    db.commit()
    return {"ok": True}
