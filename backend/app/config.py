from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional
import os

class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60*24
    ALGORITHM: str = "HS256"
    DATABASE_URL: Optional[str] = None
    ADMIN_PHONE: Optional[str] = None
    MERCHANT_SIGNUP_CODE: Optional[str] = None
    DEV_RETURN_OTP_IN_RESPONSE: bool = True

    @field_validator("DEV_RETURN_OTP_IN_RESPONSE", mode="before")
    @classmethod
    def parse_bool(cls, v):
        if isinstance(v, bool): return v
        if v is None: return False
        return str(v).lower() in {"1","true","yes","y"}

settings = Settings(_env_file=os.path.join(os.path.dirname(__file__), "..", ".env"))
