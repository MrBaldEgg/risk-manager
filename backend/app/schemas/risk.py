from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.risk import RiskCategory, RiskPriority


class RiskBase(BaseModel):
    """Базовая схема риска"""
    title: str = Field(..., min_length=1, max_length=500, example="Уход ключевого сотрудника")
    description: Optional[str] = Field(None, example="Потеря ведущего разработчика может остановить проект")
    category: RiskCategory = Field(default=RiskCategory.PERSONNEL)
    probability: int = Field(default=3, ge=1, le=5, description="Вероятность (1-5)")
    impact: int = Field(default=3, ge=1, le=5, description="Влияние (1-5)")


class RiskCreate(RiskBase):
    """Схема для создания риска"""
    project_id: str


class RiskUpdate(BaseModel):
    """Схема для обновления риска"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    category: Optional[RiskCategory] = None
    probability: Optional[int] = Field(None, ge=1, le=5)
    impact: Optional[int] = Field(None, ge=1, le=5)


class RiskResponse(RiskBase):
    """Схема для ответа"""
    id: str
    project_id: str
    priority: Optional[RiskPriority] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)