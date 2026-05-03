from sqlalchemy import Column, String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum

#Сатус
class ProjectStatus(str, enum.Enum):
    DRAFT = "draft"             # Черновик
    IN_ANALYSIS = "in_analysis"  # В процессе анализа
    COMPLETED = "completed"    # Анализ завершен
    ARCHIVED = "archived"      # В архиве

#Сфера бизнеса (для классификация для более точного анализа)
class BusinessSphere(str, enum.Enum):
    RETAIL = "retail"              # Торговля
    SERVICES = "services"          # Услуги
    PRODUCTION = "production"     # Производство
    IT = "it"                      # IT
    CONSTRUCTION = "construction"  # Строительство
    LOGISTICS = "logistics"       # Логистика
    FINANCE = "finance"           # Финансы
    OTHER = "other"               # Другое

#Проект
class Project(Base):
    
    __tablename__ = "projects"
    
    # Основные поля
    id = Column(String(36), primary_key=True, index=True)
    
    name = Column(
        String(255),
        nullable=False,
        comment="Название проекта"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Краткое описание"
    )
    
    sphere = Column(
        SQLEnum(BusinessSphere),
        default=BusinessSphere.OTHER,
        nullable=False,
        comment="Сфера бизнеса"
    )
    
    status = Column(
        SQLEnum(ProjectStatus),
        default=ProjectStatus.DRAFT,
        nullable=False,
        comment="Статус проекта"
    )
    
    # Связь с владельцем
    owner_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID владельца проекта"
    )
    
    # Отношения (автоматичесское заполнение)
    owner = relationship("User", back_populates="projects")
    risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
    analyses = relationship("RiskAnalysis", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Project(id={self.id}, name={self.name}, status={self.status})>"