from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.config import get_settings
from core.database import get_db
from core.security import get_current_user, get_current_user_optional, verify_password
from models.user import User
from schemas.auth import (
    AccessTokenResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    UpdatePasswordRequest,
)
from services.email_service import send_password_reset_email
from services.auth_service import (
    authenticate_user,
    create_password_reset_token,
    find_user_by_email,
    get_valid_reset_request,
    issue_tokens,
    mark_reset_token_used,
    refresh_access_token,
    register_user,
    revoke_refresh_token,
    revoke_user_refresh_tokens,
    update_user_password,
)

router = APIRouter()
settings = get_settings()


@router.get("/health")
def auth_health() -> dict[str, str]:
    return {"message": "auth routes ready"}


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    user = find_user_by_email(db, payload.email)
    if user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    register_user(db, payload.email, payload.password)
    return MessageResponse(message="User registered successfully")


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    access_token, refresh_token = issue_tokens(db, user)
    return LoginResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=AccessTokenResponse)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    access_token = refresh_access_token(db, payload.refresh_token)
    if not access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse)
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    revoked = revoke_refresh_token(db, payload.refresh_token)
    if not revoked:
        revoke_user_refresh_tokens(db, current_user.id)
    return MessageResponse(message="Logged out successfully")


@router.post("/forgot-password", response_model=MessageResponse)
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = find_user_by_email(db, payload.email)
    if not user:
        return MessageResponse(message="If the email exists, a reset link was sent")
    token = create_password_reset_token(db, user)
    reset_link = f"{settings.password_reset_base_url}?token={token}"
    send_password_reset_email(user.email, reset_link)
    return MessageResponse(message="If the email exists, a reset link was sent")


@router.post("/update-password", response_model=MessageResponse)
def update_password(
    payload: UpdatePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    # Token-based password reset (forgot password flow)
    if payload.token:
        reset_row = get_valid_reset_request(db, payload.token)
        if not reset_row:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")
        user = db.query(User).filter(User.id == reset_row.user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        update_user_password(db, user, payload.new_password)
        mark_reset_token_used(db, reset_row)
        revoke_user_refresh_tokens(db, user.id)
        return MessageResponse(message="Password reset successfully")
    
    # Authenticated password update
    if not current_user or not current_user.hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not payload.current_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password required")
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
    update_user_password(db, current_user, payload.new_password)
    revoke_user_refresh_tokens(db, current_user.id)
    return MessageResponse(message="Password updated successfully")

