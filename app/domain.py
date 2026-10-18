from datetime import date
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppError(Exception):
    """Base exception class for application errors."""

    code: str = "INTERNAL_ERROR"
    status_code = 500

    def __init__(
        self, message: str, *, code: str | None = None, status_code: int | None = None
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code


class ValidationError(AppError):
    """Raised when a domain validation rule fails."""

    code: str = "VALIDATION_ERROR"
    status_code = 422


class AuthenticationError(AppError):
    code = "UNAUTHENTICATED"
    status_code = 401


class ConflictError(AppError):
    code = "CONFLICT"
    status_code = 409


ALLOWED_TRANSITIONS: dict[TaskStatus, set[TaskStatus]] = {
    TaskStatus.PENDING: {TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED},
    TaskStatus.IN_PROGRESS: {
        TaskStatus.PENDING,
        TaskStatus.COMPLETED,
        TaskStatus.CANCELLED,
    },
    TaskStatus.COMPLETED: {TaskStatus.IN_PROGRESS},
    TaskStatus.CANCELLED: {TaskStatus.PENDING},
}


def check_transition(current: TaskStatus, new: TaskStatus) -> None:
    """
    Check if transitioning from `current` status to `new` status is valid.
    Idempotent if `current == new`.
    Raises ValidationError if the transition is invalid.
    """
    if current == new:
        return

    allowed = ALLOWED_TRANSITIONS.get(current, set())
    if new not in allowed:
        raise ValidationError(
            f"Không thể chuyển trạng thái từ '{current.value}' sang '{new.value}'"
        )


def check_dates(start: date | None, due: date | None) -> None:
    """
    Check if dates are valid.
    Raises ValidationError if `due` is before `start`.
    If either `start` or `due` is None, it is valid.
    """
    if start is not None and due is not None:
        if due < start:
            raise ValidationError(
                f"Ngày kết thúc ({due}) không được trước ngày bắt đầu ({start})"
            )
