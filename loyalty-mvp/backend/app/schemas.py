from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class OTPRequest(BaseModel):
    phone: str
    name: Optional[str] = None
    email: Optional[str] = None
    dob: Optional[date] = None

class OTPVerify(BaseModel):
    phone: str
    code: str

class SetPIN(BaseModel):
    pin: str = Field(min_length=4, max_length=4)

class UserOut(BaseModel):
    id: str
    phone_e164: str
    name: str
    email: Optional[str] = None
    dob: Optional[date] = None
    role: str

class MerchantCreate(BaseModel):
    cafe_name: str
    logo_url: Optional[str] = None
    location_text: Optional[str] = None
    stamps_required: int = 9
    signup_code: str

class MerchantOut(BaseModel):
    id: str
    cafe_name: str
    logo_url: Optional[str]
    location_text: Optional[str]
    stamps_required: int
    is_active: bool

class EnrollmentOut(BaseModel):
    enrollment_id: str
    merchant: MerchantOut
    stamps_count: int
    stamps_required: int
    total_stamps: int

class StampAdd(BaseModel):
    merchant_id: str
    customer_phone: str

class RedeemRequestIn(BaseModel):
    merchant_id: str

class RedeemApproveIn(BaseModel):
    redemption_id: str

class RedemptionOut(BaseModel):
    id: str
    status: str
    merchant_id: str
    merchant_name: str
    requested_at: datetime
