from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..database import get_db
from .. import models
from ..auth_utils import require_role

router = APIRouter(prefix="/reports", tags=["reports"])

@router.get("/stamps")
def stamps_report(range: str = "day", merchant=Depends(require_role(models.RoleEnum.MERCHANT, models.RoleEnum.ADMIN)), db: Session = Depends(get_db)):
    m = db.query(models.Merchant).filter(models.Merchant.owner_user_id==merchant.id).first()
    if not m:
        return {"count": 0}
    now = datetime.utcnow()
    if range == "week":
        since = now - timedelta(days=7)
    elif range == "month":
        since = now - timedelta(days=30)
    else:
        since = now - timedelta(days=1)
    count = db.query(models.Stamp).join(models.Enrollment, models.Stamp.enrollment_id==models.Enrollment.id) \
            .filter(models.Enrollment.merchant_id==m.id, models.Stamp.created_at>=since).count()
    return {"count": count}
