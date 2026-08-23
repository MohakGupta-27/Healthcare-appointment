from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User, UserRole
from app.repositories.user import create_user, get_user_by_email
from app.schemas.auth import TokenResponse, UserCreate, UserOut


def register_user(db: Session, data: UserCreate) -> UserOut:
    existing = get_user_by_email(db, data.email.lower())
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    user = User(
        email=data.email.lower(),
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole.patient,
    )
    created = create_user(db, user)
    return UserOut.model_validate(created)


def login_user(db: Session, email: str, password: str) -> TokenResponse:
    user = get_user_by_email(db, email.lower())
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )
    token = create_access_token(subject=user.id, role=user.role.value)
    return TokenResponse(access_token=token)
