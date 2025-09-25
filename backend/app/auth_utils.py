from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from .config import settings
from .database import get_db
from . import models

SESSION_COOKIE_NAME = "annicard_session"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt, int(expires_delta.total_seconds()) if expires_delta else 60*60*24*7

def set_session_cookie(response: Response, token: str, max_age: int):
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        httponly=True,
        max_age=max_age,
        samesite="lax",
        secure=settings.SESSION_COOKIE_SECURE,
        path="/",
    )

def clear_session_cookie(response: Response):
    response.delete_cookie(SESSION_COOKIE_NAME, path="/")

def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Bad token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Bad token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_role(*roles):
    def dependency(user: models.User = Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency

def hash_pin(pin: str) -> str:
    return bcrypt.hash(pin)

def verify_pin(pin: str, hashed: str) -> bool:
    return bcrypt.verify(pin, hashed)
