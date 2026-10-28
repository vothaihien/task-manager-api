from collections.abc import Iterator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.domain import AuthenticationError
from app.models import User
from app.security import decode_access_token


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AuthenticationError("Missing bearer token", code="UNAUTHENTICATED")
    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise AuthenticationError("Invalid or expired token", code="UNAUTHENTICATED")
    user = db.scalar(
        select(User).where(User.id == user_id, User.deleted_at.is_(None))
    )
    if user is None:
        raise AuthenticationError(
            "User not found or has been deleted", code="UNAUTHENTICATED"
        )
    return user
