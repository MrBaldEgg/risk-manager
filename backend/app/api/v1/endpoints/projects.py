import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.user import User
from app.models.project import Project, ProjectStatus
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/projects", tags=["projects"])


# CRUD для проектов

@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Создание нового проекта.
    - name: Название
    - description: Описание 
    - sphere: Сфера бизнеса
    """
    project = Project(
        id=str(uuid.uuid4()),
        name=project_in.name,
        description=project_in.description,
        sphere=project_in.sphere,
        owner_id=current_user.id,
        status=ProjectStatus.DRAFT
    )
    
    db.add(project)
    await db.commit()
    await db.refresh(project)
    
    return project


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    skip: int = 0,
    limit: int = 100
):
    """
    Список проектов текущего пользователя.
    - skip: Пропустить N записей (для пагинации)
    - limit: Максимальное количество записей
    """
    result = await db.execute(
        select(Project)
        .where(Project.owner_id == current_user.id)
        .order_by(Project.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    projects = result.scalars().all()
    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение информации о конкретном проекте.
    Только владелец имеет доступ.
    """
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_in: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновление проекта.
    Обновляются только переданные поля.
    """
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    # Обновляем только переданные поля
    update_data = project_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)
    
    await db.commit()
    await db.refresh(project)
    
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удаление проекта.
    Удаляются также все связанные риски (каскадное удаление).
    """
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    await db.delete(project)
    await db.commit()
    
    return None