"""Exercise database connectivity and PostgreSQL-enforced model constraints.

Run with: python scripts/db_smoke.py
"""

from datetime import date
from pathlib import Path
import sys
from typing import Callable, NamedTuple
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, configure_mappers

from app.database import Base, SessionLocal, engine
from app.models import Project, ProjectMember, Task, User

failures = 0


class ScenarioData(NamedTuple):
    user_id: uuid.UUID
    project_id: uuid.UUID
    outsider_id: uuid.UUID
    role_user_id: uuid.UUID
    owner_candidate_id: uuid.UUID
    owner_email: str


def test_models_metadata() -> None:
    print("[1/3] Validating SQLAlchemy models and mappers...")
    configure_mappers()

    expected_tables = {"users", "projects", "project_members", "tasks"}
    actual_tables = set(Base.metadata.tables)
    missing_tables = expected_tables - actual_tables
    if missing_tables:
        raise AssertionError(f"Missing tables: {missing_tables}")
    print(f"  [PASS] Found tables: {', '.join(sorted(actual_tables))}")


def test_db_connection() -> None:
    print("[2/3] Testing database connection and creating tables...")
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1")).scalar_one()
        if result != 1:
            raise AssertionError(f"Unexpected SELECT 1 result: {result}")
    Base.metadata.create_all(bind=engine)
    print("  [PASS] Database connection successful; all tables created")


def create_valid_data() -> ScenarioData:
    print("[3/3] Creating valid data and verifying it with SELECT...")
    suffix = uuid.uuid4().hex
    user_id = uuid.uuid4()
    project_id = uuid.uuid4()
    member_id = uuid.uuid4()
    task_id = uuid.uuid4()
    unassigned_task_id = uuid.uuid4()
    outsider_id = uuid.uuid4()
    role_user_id = uuid.uuid4()
    owner_candidate_id = uuid.uuid4()

    user = User(
        id=user_id,
        email=f"owner-{suffix}@example.com",
        password_hash="smoke-test",
    )
    project = Project(
        id=project_id,
        created_by_id=user_id,
        name=f"Smoke test project {suffix}",
    )
    owner_membership = ProjectMember(
        id=member_id,
        project_id=project_id,
        user_id=user_id,
        role="owner",
    )
    assigned_task = Task(
        id=task_id,
        project_id=project_id,
        assigned_to_user_id=user_id,
        name=f"Assigned smoke task {suffix}",
    )
    unassigned_task = Task(
        id=unassigned_task_id,
        project_id=project_id,
        assigned_to_user_id=None,
        name=f"Unassigned smoke task {suffix}",
    )
    outsider = User(
        id=outsider_id,
        email=f"outsider-{suffix}@example.com",
        password_hash="smoke-test",
    )
    role_user = User(
        id=role_user_id,
        email=f"role-{suffix}@example.com",
        password_hash="smoke-test",
    )
    owner_candidate = User(
        id=owner_candidate_id,
        email=f"owner-candidate-{suffix}@example.com",
        password_hash="smoke-test",
    )

    with SessionLocal() as session:
        session.add_all(
            [
                user,
                project,
                owner_membership,
                assigned_task,
                unassigned_task,
                outsider,
                role_user,
                owner_candidate,
            ]
        )
        session.commit()

    with SessionLocal() as session:
        stored_user = session.scalar(select(User).where(User.id == user_id))
        stored_project = session.scalar(
            select(Project).where(Project.id == project_id)
        )
        stored_membership = session.scalar(
            select(ProjectMember).where(ProjectMember.id == member_id)
        )
        stored_task = session.scalar(select(Task).where(Task.id == task_id))
        stored_unassigned_task = session.scalar(
            select(Task).where(Task.id == unassigned_task_id)
        )
        assert stored_user is not None
        assert stored_project is not None
        assert stored_membership is not None
        assert stored_task is not None
        assert stored_unassigned_task is not None
        assert stored_task.assigned_to_user_id == stored_user.id
        assert stored_unassigned_task.assigned_to_user_id is None
        print(
            "  [PASS] SELECT user/project/owner/task: "
            f"{stored_user.email}, {stored_project.name}, "
            f"{stored_membership.role}, {stored_task.name}"
        )
        print(
            "  [PASS] SELECT unassigned task: "
            f"{stored_unassigned_task.name} "
            f"(assigned_to_user_id={stored_unassigned_task.assigned_to_user_id})"
        )

    return ScenarioData(
        user_id=user_id,
        project_id=project_id,
        outsider_id=outsider_id,
        role_user_id=role_user_id,
        owner_candidate_id=owner_candidate_id,
        owner_email=f"owner-{suffix}@example.com",
    )


def expect_violation(
    label: str,
    action: Callable[[Session], None],
    expected_constraint: str,
) -> None:
    global failures

    with SessionLocal() as session:
        try:
            action(session)
            session.flush()
        except IntegrityError as error:
            session.rollback()
            diagnostic = getattr(error.orig, "diag", None)
            actual_constraint = getattr(diagnostic, "constraint_name", None)
            ok = actual_constraint == expected_constraint
            print(
                f"  {'[PASS]' if ok else '[FAIL]'} {label}: "
                f"{actual_constraint} (expected {expected_constraint})"
            )
            failures += 0 if ok else 1
        else:
            session.rollback()
            print(f"  [FAIL] {label}: violation was not rejected")
            failures += 1


def test_constraints(data: ScenarioData) -> None:
    suffix = uuid.uuid4().hex
    project_id = data.project_id

    def duplicate_email(session: Session) -> None:
        session.add(
            User(
                email=data.owner_email,
                password_hash="smoke-test",
            )
        )

    def invalid_role(session: Session) -> None:
        session.add(
            ProjectMember(
                project_id=project_id,
                user_id=data.role_user_id,
                role="admin",
            )
        )

    def duplicate_active_owner(session: Session) -> None:
        session.add(
            ProjectMember(
                project_id=project_id,
                user_id=data.owner_candidate_id,
                role="owner",
            )
        )

    def invalid_task_dates(session: Session) -> None:
        session.add(
            Task(
                project_id=project_id,
                name=f"Invalid dates {suffix}",
                start_date=date(2026, 10, 2),
                due_date=date(2026, 10, 1),
            )
        )

    def nonmember_assignee(session: Session) -> None:
        session.add(
            Task(
                project_id=project_id,
                assigned_to_user_id=data.outsider_id,
                name=f"Nonmember assignee {suffix}",
            )
        )

    def mixed_case_email(session: Session) -> None:
        session.add(
            User(
                email=f"Mixed-{suffix}@example.com",
                password_hash="smoke-test",
            )
        )

    def blank_project_name(session: Session) -> None:
        session.add(
            Project(
                created_by_id=data.user_id,
                name="   ",
            )
        )

    def blank_task_name(session: Session) -> None:
        session.add(Task(project_id=project_id, name="   "))

    expect_violation(
        "duplicate user email", duplicate_email, "uq_users_email"
    )
    expect_violation(
        "invalid project membership role",
        invalid_role,
        "ck_project_members_role",
    )
    expect_violation(
        "second active project owner",
        duplicate_active_owner,
        "uq_project_members_active_owner",
    )
    expect_violation(
        "due date before start date", invalid_task_dates, "ck_tasks_dates"
    )
    expect_violation(
        "assign task to nonmember",
        nonmember_assignee,
        "fk_tasks_assignee_member",
    )
    expect_violation(
        "non-lowercase email",
        mixed_case_email,
        "ck_users_email_lowercase",
    )
    expect_violation(
        "blank project name",
        blank_project_name,
        "ck_projects_name_nonempty",
    )
    expect_violation(
        "blank task name",
        blank_task_name,
        "ck_tasks_name_nonempty",
    )


def main() -> None:
    try:
        test_models_metadata()
        test_db_connection()
        data = create_valid_data()
        test_constraints(data)
    except Exception as error:
        print(f"[FAIL] Smoke test failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    if failures:
        print(f"\n[FAIL] Smoke test failed: {failures} constraint check(s) failed.")
        raise SystemExit(1)

    print("\n[PASS] Smoke test finished successfully!")


if __name__ == "__main__":
    main()
