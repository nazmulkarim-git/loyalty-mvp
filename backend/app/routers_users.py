from fastapi import APIRouter, Depends
from . import models
from .schemas import UserOut
from .auth_utils import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me", response_model=UserOut)
def get_me(current: models.User = Depends(get_current_user)):
    return UserOut(
        id=current.id, phone_e164=current.phone_e164, name=current.name,
        email=current.email, dob=current.dob, role=current.role
    )
