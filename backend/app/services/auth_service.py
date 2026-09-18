from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from app.models.notification import NotificationPreference
from app.models.profile import Profile
from app.models.user import User


class AuthError(Exception):
    pass


def register_user(db: Session, full_name: str, email: str, password: str) -> User:
    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        raise AuthError("An account with this email already exists.")

    user = User(email=email.lower(), full_name=full_name, hashed_password=hash_password(password))
    db.add(user)
    db.flush()

    db.add(Profile(user_id=user.id))
    db.add(NotificationPreference(user_id=user.id))
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Incorrect email or password.")
    if not user.is_active:
        raise AuthError("This account has been deactivated.")
    return user


def issue_tokens(user: User) -> tuple[str, str]:
    return create_access_token(user.id), create_refresh_token(user.id)
