from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .database import get_db
from . import models
from .schemas import EnrollmentOut, MerchantOut
from .auth_utils import get_current_user

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

@router.get("/my", response_model=list[EnrollmentOut])
def my_enrollments(current=Depends(get_current_user), db: Session = Depends(get_db)):
    ens = db.query(models.Enrollment).filter(models.Enrollment.user_id==current.id).all()
    result = []
    for e in ens:
        m = db.query(models.Merchant).filter(models.Merchant.id==e.merchant_id).first()
        result.append(EnrollmentOut(
            enrollment_id=e.id,
            merchant=MerchantOut(id=m.id, cafe_name=m.cafe_name, logo_url=m.logo_url, location_text=m.location_text, stamps_required=m.stamps_required, is_active=m.is_active),
            stamps_count=e.stamps_count, stamps_required=m.stamps_required, total_stamps=e.total_stamps
        ))
    return result
