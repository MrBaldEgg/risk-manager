import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.risk import Risk
from app.schemas.risk import RiskCreate, RiskUpdate, RiskResponse
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/projects/{project_id}/risks", tags=["risks"])


async def get_project_or_404(
    project_id: str,
    user_id: str,
    db: AsyncSession
) -> Project:
    """Вспомогательная функция — получить проект или 404"""
    result = await db.execute(
        select(Project).where(
            Project.id == project_id,
            Project.owner_id == user_id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    return project


# CRUD для рисков

@router.post("/", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def add_risk_to_project(
    project_id: str,
    risk_in: RiskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Добавление риска к проекту.
    
    - title: Краткое название
    - description: Подробное описание
    - category: Категория риска
    - probability: Вероятность (1-5)
    - impact: Влияние (1-5)
    """
    # Проверка существования проекта
    project = await get_project_or_404(project_id, current_user.id, db)
    
   
    risk = Risk(
        id=str(uuid.uuid4()),
        title=risk_in.title,
        description=risk_in.description,
        category=risk_in.category,
        probability=risk_in.probability,
        impact=risk_in.impact,
        project_id=project.id
    )
    
    # Подсчет приоритета риска
    risk.calculate_priority()
    
    db.add(risk)
    await db.commit()
    await db.refresh(risk)
    
    return risk


@router.get("/", response_model=List[RiskResponse])
async def list_project_risks(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Список всех рисков проекта.
    """
    await get_project_or_404(project_id, current_user.id, db)
    
    result = await db.execute(
        select(Risk)
        .where(Risk.project_id == project_id)
        .order_by(Risk.created_at.desc())
    )
    risks = result.scalars().all()
    return risks


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    project_id: str,
    risk_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Получение информации о конкретном риске.
    """
    await get_project_or_404(project_id, current_user.id, db)
    
    result = await db.execute(
        select(Risk).where(
            Risk.id == risk_id,
            Risk.project_id == project_id
        )
    )
    risk = result.scalar_one_or_none()
    
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Риск не найден"
        )
    
    return risk


@router.patch("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    project_id: str,
    risk_id: str,
    risk_in: RiskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Обновление риска.
    
    При изменении probability/impact автоматически пересчитывается приоритет.
    """
    await get_project_or_404(project_id, current_user.id, db)
    
    result = await db.execute(
        select(Risk).where(
            Risk.id == risk_id,
            Risk.project_id == project_id
        )
    )
    risk = result.scalar_one_or_none()
    
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Риск не найден"
        )
    

    update_data = risk_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(risk, field, value)
    
    # Пересчет приоритета риска автоматически после изменения параметров
    if "probability" in update_data or "impact" in update_data:
        risk.calculate_priority()
    
    await db.commit()
    await db.refresh(risk)
    
    return risk


@router.delete("/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk(
    project_id: str,
    risk_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Удаление риска.
    """
    await get_project_or_404(project_id, current_user.id, db)
    
    result = await db.execute(
        select(Risk).where(
            Risk.id == risk_id,
            Risk.project_id == project_id
        )
    )
    risk = result.scalar_one_or_none()
    
    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Риск не найден"
        )
    
    await db.delete(risk)
    await db.commit()
    
    return None