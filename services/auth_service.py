from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from core.config import get_settings
from core.security import (
    create_access_token,
    generate_refresh_token,
    generate_reset_token,
    hash_password,
    hash_token,
    verify_password,
)
from models.password_reset import PasswordResetToken
from models.refresh_token import RefreshToken
from models.user import User


settings = get_settings()


def _ensure_aware(dt: datetime) -> datetime:
    """Ensure datetime is timezone-aware (UTC)"""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def register_user(db: Session, email: str, password: str) -> User:
    user = User(email=email, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def issue_tokens(db: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(subject=str(user.id))
    raw_refresh_token = generate_refresh_token()
    refresh_row = RefreshToken(
        user_id=user.id,
        token_hash=hash_token(raw_refresh_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
        revoked=False,
    )
    db.add(refresh_row)
    db.commit()
    return access_token, raw_refresh_token


def create_password_reset_token(db: Session, user: User) -> str:
    token = generate_reset_token()
    token_hash = hash_token(token)
    reset_row = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.reset_token_expire_minutes),
    )
    db.add(reset_row)
    db.commit()
    return token


def get_valid_reset_request(db: Session, token: str) -> PasswordResetToken | None:
    token_hash = hash_token(token)
    reset_row = db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first()
    if not reset_row or reset_row.used:
        return None
    if _ensure_aware(reset_row.expires_at) < datetime.now(timezone.utc):
        return None
    return reset_row


def mark_reset_token_used(db: Session, reset_row: PasswordResetToken) -> None:
    reset_row.used = True
    db.add(reset_row)
    db.commit()


def update_user_password(db: Session, user: User, new_password: str) -> None:
    user.hashed_password = hash_password(new_password)
    db.add(user)
    db.commit()


def find_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def refresh_access_token(db: Session, raw_refresh_token: str) -> str | None:
    token_hash = hash_token(raw_refresh_token)
    refresh_row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not refresh_row or refresh_row.revoked:
        return None
    if _ensure_aware(refresh_row.expires_at) < datetime.now(timezone.utc):
        return None
    return create_access_token(subject=str(refresh_row.user_id))


def revoke_refresh_token(db: Session, raw_refresh_token: str) -> bool:
    token_hash = hash_token(raw_refresh_token)
    refresh_row = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not refresh_row:
        return False
    refresh_row.revoked = True
    db.add(refresh_row)
    db.commit()
    return True


def revoke_user_refresh_tokens(db: Session, user_id: int) -> None:
    rows = db.query(RefreshToken).filter(RefreshToken.user_id == user_id, RefreshToken.revoked.is_(False)).all()
    for row in rows:
        row.revoked = True
        db.add(row)
    db.commit()
