from datetime import date
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AppError(Exception):
    """Base exception class for application errors."""

    pass


class ValidationError(AppError):
    """Raised when a domain validation rule fails."""

    pass


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
            f"Invalid status transition from '{current.value}' to '{new.value}'"
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
                f"Due date ({due}) cannot be before start date ({start})"
            )
