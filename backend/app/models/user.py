# app/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"           # Администратор (управление пользователями)
    ENTREPRENEUR = "entrepreneur"  # Обычный предприниматель (зарегистрированный пользователь)
    GUEST = "guest"            # Гость (ограниченный доступ)

class User(Base):
    
    __tablename__ = "users"  
    
    # Основные поля
    id = Column(String(36), primary_key=True, index=True)  # UUID как строка
    
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
        comment="Email пользователя (логин)"
    )
    
    hashed_password = Column(
        String(255),
        nullable=False,
        comment="Хеш пароля (bcrypt)"
    )
    
    full_name = Column(
        String(255),
        nullable=True,
        comment="Полное имя пользователя"
    )
    
    # Статус и роль
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Активен ли аккаунт"
    )
    
    is_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Подтвержден ли email"
    )
    
    role = Column(
        SQLEnum(UserRole),
        default=UserRole.ENTREPRENEUR,
        nullable=False,
        comment="Роль пользователя"
    )
    
    # Дополнительная информация
    company_name = Column(
        String(255),
        nullable=True,
        comment="Название компании (если есть)"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        comment="Контактный телефон"
    )
    
    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Дата последнего входа"
    )
    
    # Связи с другими таблицами (будут позже)
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan",lazy="selectin")
    
    def __repr__(self):
        """Строковое представление объекта (для отладки)"""
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"