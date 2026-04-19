from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional
from app.models.user import UserRole


# ============== Базовые схемы ==============

class UserBase(BaseModel):
    """Базовая схема с общими полями"""
    email: EmailStr
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None


# ============== Схемы для запросов ==============

class UserCreate(UserBase):
    """Схема для регистрации нового пользователя"""
    password: str = Field(..., min_length=8, max_length=72)


class UserUpdate(BaseModel):
    """Схема для обновления профиля (все поля опциональны)"""
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """Схема для входа в систему"""
    email: EmailStr
    password: str


class PasswordChange(BaseModel):
    """Схема для смены пароля"""
    old_password: str
    new_password: str = Field(..., min_length=8, max_length=72)


# ============== Схемы для ответов ==============

class UserResponse(UserBase):
    """Схема для ответа с данными пользователя (без пароля!)"""
    id: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserInDB(UserResponse):
    """Внутренняя схема с хешем пароля"""
    hashed_password: str


class UserListResponse(BaseModel):
    """Схема для списка пользователей"""
    users: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int