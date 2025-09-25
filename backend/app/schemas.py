from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class UserOut(BaseModel):
    id: str
    phone_e164: str
    name: str
    email: Optional[str] = None
    dob: Optional[date] = None
    role: str

class CustomerSignupIn(BaseModel):
    name: str
    phone: str
    pin: str = Field(min_length=4, max_length=4)
    confirm_pin: str = Field(min_length=4, max_length=4)
    dob: date

class CustomerSigninIn(BaseModel):
    phone: str
    pin: str = Field(min_length=4, max_length=4)

class CustomerProfileUpdateIn(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    pin: Optional[str] = Field(default=None, min_length=4, max_length=4)
    confirm_pin: Optional[str] = Field(default=None, min_length=4, max_length=4)
    dob: Optional[date] = None

class MerchantSignupIn(BaseModel):
    business_name: str
    business_type: str
    owner_name: str
    phone: str
    pin: str = Field(min_length=4, max_length=4)
    confirm_pin: str = Field(min_length=4, max_length=4)
    location_text: str
    signup_code: str

class MerchantSigninIn(BaseModel):
    phone: str
    pin: str = Field(min_length=4, max_length=4)

class MerchantOut(BaseModel):
    id: str
    business_name: str
    business_type: str
    location_text: str
    stamps_required: int
    is_active: bool

class EnrollmentOut(BaseModel):
    enrollment_id: str
    merchant: MerchantOut
    stamps_count: int
    stamps_required: int
    total_stamps: int

class StampAdd(BaseModel):
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
