from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Text, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from .database import Base
import uuid

def uuid4_str():
    return str(uuid.uuid4())

class RoleEnum:
    CUSTOMER = "customer"
    MERCHANT = "merchant"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid4_str)
    phone_e164: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False, default="User")
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    dob: Mapped[Date | None] = mapped_column(Date, nullable=True)
    pin_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default=RoleEnum.CUSTOMER)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    merchants = relationship("Merchant", back_populates="owner")

class Merchant(Base):
    __tablename__ = "merchants"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid4_str)
    owner_user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    cafe_name: Mapped[str] = mapped_column(String, nullable=False)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    location_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    stamps_required: Mapped[int] = mapped_column(Integer, nullable=False, default=9)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="merchants")
    enrollments = relationship("Enrollment", back_populates="merchant")

class Enrollment(Base):
    __tablename__ = "enrollments"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid4_str)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    merchant_id: Mapped[str] = mapped_column(String, ForeignKey("merchants.id"))
    stamps_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    total_stamps: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    user = relationship("User")
    merchant = relationship("Merchant", back_populates="enrollments")

class Stamp(Base):
    __tablename__ = "stamps"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid4_str)
    enrollment_id: Mapped[str] = mapped_column(String, ForeignKey("enrollments.id"))
    merchant_user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Redemption(Base):
    __tablename__ = "redemptions"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid4_str)
    enrollment_id: Mapped[str] = mapped_column(String, ForeignKey("enrollments.id"))
    status: Mapped[str] = mapped_column(String, nullable=False, default="requested")
    requested_by: Mapped[str | None] = mapped_column(String, ForeignKey("users.id"))
    approved_by: Mapped[str | None] = mapped_column(String, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

class OTPCode(Base):
    __tablename__ = "otp_codes"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=uuid4_str)
    phone_e164: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
