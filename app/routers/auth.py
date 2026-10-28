from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config import settings
from app.dependencies import get_db
from app.domain import AuthenticationError, ConflictError
from app.models import User
from app.schemas import LoginRequest, TokenResponse, UserRead, UserCreate
from app.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# Nếu không tìm thấy user thì vẫn verify một hash giả
_DUMMY_HASH = hash_password("this_is_a_dummy_password_for_timing_attack_prevention")


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    email = payload.email.strip().lower()
    hashed = hash_password(payload.password)

    user = User(
        email=email,
        password_hash=hashed,
        full_name=payload.full_name.strip() if payload.full_name else None,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)
    except IntegrityError as error:
        db.rollback()

        diag = getattr(error.orig, "diag", None)
        constraint_name = getattr(diag, "constraint_name", None)

        if constraint_name == "uq_users_email":
            raise ConflictError(
                "Email already exists",
                code="EMAIL_ALREADY_EXISTS",
            ) from None
        raise
    return UserRead.model_validate(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    email = payload.email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == email, User.deleted_at.is_(None))
    )

    if user is not None:
        password_ok = verify_password(payload.password, user.password_hash)
    else:
        verify_password(payload.password, _DUMMY_HASH)
        password_ok = False

    if user is None or not password_ok:
        raise AuthenticationError("Invalid credentials", code="INVALID_CREDENTIALS")

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60,
    )
