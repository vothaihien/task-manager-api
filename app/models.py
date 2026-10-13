import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    String,
    Text,
    UUID,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("email = lower(email)", name="ck_users_email_lowercase"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Relationships
    created_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="created_by",
        foreign_keys="Project.created_by_id",
    )


class Project(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="ck_projects_name_nonempty"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Relationships
    created_by: Mapped["User"] = relationship(
        "User",
        back_populates="created_projects",
        foreign_keys=[created_by_id],
    )
    members: Mapped[list["ProjectMember"]] = relationship(
        "ProjectMember",
        back_populates="project",
        foreign_keys="ProjectMember.project_id",
    )
    tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="project",
        foreign_keys="Task.project_id",
    )


class ProjectMember(Base):
    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint(
            "project_id", "user_id", name="uq_project_members_project_user"
        ),
        CheckConstraint(
            "role IN ('owner', 'manager', 'member')",
            name="ck_project_members_role",
        ),
        # Partial unique index: mỗi dự án chỉ có đúng 1 owner đang hoạt động
        Index(
            "uq_project_members_active_owner",
            "project_id",
            unique=True,
            postgresql_where=text("role = 'owner' AND deleted_at IS NULL"),
        ),
        # Index hiệu năng: truy vấn danh sách dự án của user
        Index(
            "ix_project_members_user",
            "user_id",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="members",
        foreign_keys=[project_id],
    )
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
    )


class Task(Base):
    __tablename__ = "tasks"
    __table_args__ = (
        CheckConstraint("btrim(name) <> ''", name="ck_tasks_name_nonempty"),
        CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'cancelled')",
            name="ck_tasks_status",
        ),
        CheckConstraint(
            "priority IN ('low', 'medium', 'high')",
            name="ck_tasks_priority",
        ),
        CheckConstraint(
            "start_date IS NULL OR due_date IS NULL OR due_date >= start_date",
            name="ck_tasks_dates",
        ),
        # FK ghép: bảo đảm người được giao thuộc cùng dự án
        ForeignKeyConstraint(
            ["project_id", "assigned_to_user_id"],
            ["project_members.project_id", "project_members.user_id"],
            name="fk_tasks_assignee_member",
        ),
        # Index hiệu năng: phân trang theo thứ tự mới nhất trước
        Index(
            "ix_tasks_project_created",
            "project_id",
            text("created_at DESC"),
            text("id DESC"),
            postgresql_where=text("deleted_at IS NULL"),
        ),
        # Index hiệu năng: lọc theo trạng thái
        Index(
            "ix_tasks_project_status",
            "project_id",
            "status",
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id"),
        nullable=False,
    )
    assigned_to_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        default=None,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True, default=None)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        server_default=text("'pending'"),
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
        server_default=text("'medium'"),
    )
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True, default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks",
        foreign_keys=[project_id],
    )
