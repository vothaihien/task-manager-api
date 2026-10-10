import math
from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas import PageResponse, ProjectCreate, ProjectRead

router = APIRouter(prefix="/api/v1/projects", tags=["projects"])

# TẠM THỜI: Database lưu trữ trên bộ nhớ (in-memory) phục vụ thử nghiệm
projects_db: dict[UUID, ProjectRead] = {}


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate) -> ProjectRead:
    project = ProjectRead(
        id=uuid4(),
        name=payload.name,
        description=payload.description,
        created_at=datetime.now(timezone.utc),
    )
    projects_db[project.id] = project
    return project


@router.get("", response_model=PageResponse[ProjectRead])
async def list_projects(
    page: int = Query(default=1, ge=1, description="Số trang, bắt đầu từ 1"),
    page_size: int = Query(
        default=20, ge=1, le=100, description="Số mục trên mỗi trang (1-100)"
    ),
) -> PageResponse[ProjectRead]:
    sorted_projects = sorted(
        projects_db.values(),
        key=lambda p: (p.created_at, p.id),
        reverse=True,
    )
    total = len(sorted_projects)
    total_pages = math.ceil(total / page_size) if total > 0 else 0
    start = (page - 1) * page_size
    end = start + page_size
    items = sorted_projects[start:end]

    return PageResponse[ProjectRead](
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID) -> ProjectRead:
    project = projects_db.get(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project

