from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
import os

default_sqlite_url = f"sqlite:///" + os.path.join(os.path.dirname(__file__), "..", "loyalty.db")
DATABASE_URL = settings.DATABASE_URL or default_sqlite_url

engine = create_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
