from typing import Optional
from passlib.hash import django_pbkdf2_sha256
from sqlalchemy.orm import Session
from .models import User


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    try:
        return django_pbkdf2_sha256.verify(plain_password, hashed_password)
    except Exception:
        return False


def hash_password(plain_password: str) -> str:
    return django_pbkdf2_sha256.hash(plain_password)


def get_user_by_tracker_token(db: Session, token: str) -> Optional[User]:
    if not token:
        return None
    return db.query(User).filter(User.tracker_token == token).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def parse_auth_token(authorization: Optional[str]) -> Optional[str]:
    if not authorization:
        return None
    if authorization.startswith("Token "):
        return authorization.replace("Token ", "", 1).strip()
    if authorization.startswith("Bearer "):
        return authorization.replace("Bearer ", "", 1).strip()
    return None
