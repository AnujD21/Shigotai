from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.rate_limit import rate_limit
from app.core.security import (
    create_email_verification_token,
    create_password_reset_token,
    decode_token,
    hash_password,
)
from app.database.session import get_db
from app.models.user import User
from app.notifications.provider import get_email_provider
from app.schemas.auth import (
    EmailVerifyConfirm,
    LoginRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services.auth_service import AuthError, authenticate_user, issue_tokens, register_user

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit(5))],
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        user = register_user(db, payload.full_name, payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    verify_token = create_email_verification_token(user.id)
    get_email_provider().send_email(
        user.email,
        "Verify your Shigotai account",
        f'<p>Welcome to Shigotai. Verify your email: <a href="{settings.frontend_base_url}/verify-email?token={verify_token}">Verify Email</a></p>',
        f"Welcome to Shigotai. Verify your email using this token: {verify_token}",
    )
    access, refresh = issue_tokens(user)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit(10))])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = authenticate_user(db, payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc

    from datetime import datetime, timezone

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    access, refresh = issue_tokens(user)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    # Stateless JWTs: the client discards its tokens. A refresh-token
    # denylist would live here if longer-lived sessions are added later.
    return None


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post(
    "/password-reset/request",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limit(5))],
)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email.lower()).first()
    if user:
        token = create_password_reset_token(user.id)
        get_email_provider().send_email(
            user.email,
            "Reset your Shigotai password",
            f'<p>Reset your password: <a href="{settings.frontend_base_url}/reset-password?token={token}">Reset Password</a></p>',
            f"Reset your password using this token: {token}",
        )
    # Always return 202 regardless of whether the email exists, to avoid
    # leaking account existence.
    return {"detail": "If an account exists for this email, a reset link has been sent."}


@router.post("/password-reset/confirm", status_code=status.HTTP_204_NO_CONTENT)
def confirm_password_reset(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    token_data = decode_token(payload.token)
    if not token_data or token_data.get("type") != "password_reset":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")
    user = db.query(User).filter(User.id == token_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token.")
    user.hashed_password = hash_password(payload.new_password)
    db.commit()
    return None


@router.post("/verify-email", status_code=status.HTTP_204_NO_CONTENT)
def verify_email(payload: EmailVerifyConfirm, db: Session = Depends(get_db)):
    token_data = decode_token(payload.token)
    if not token_data or token_data.get("type") != "email_verify":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token.")
    user = db.query(User).filter(User.id == token_data["sub"]).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token.")
    user.is_email_verified = True
    db.commit()
    return None
