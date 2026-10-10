from datetime import datetime
from typing import Annotated, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, StringConstraints

NameStr = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
    ),
]


class ProjectCreate(BaseModel):
    name: NameStr
    description: str | None = None


class ProjectRead(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    created_at: datetime


T = TypeVar("T")


class PageResponse(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
    total_pages: int
