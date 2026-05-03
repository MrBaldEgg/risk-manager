from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.project import ProjectStatus, BusinessSphere


class ProjectBase(BaseModel):
    """Базовая схема проекта"""
    name: str = Field(..., min_length=1, max_length=255, example="Кофейня на Ленина")
    description: Optional[str] = Field(None, example="Открытие кофейни в центре Томска")
    sphere: BusinessSphere = Field(default=BusinessSphere.OTHER)


class ProjectCreate(ProjectBase):
    """Схема для создания проекта"""
    pass


class ProjectUpdate(BaseModel):
    """Схема для обновления проекта"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    sphere: Optional[BusinessSphere] = None
    status: Optional[ProjectStatus] = None


class ProjectResponse(ProjectBase):
    """Схема для ответа"""
    id: str
    owner_id: str
    status: ProjectStatus
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)