from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class RiskCategory(str, enum.Enum):
    OPERATIONAL = "operational"      # Операционные
    FINANCIAL = "financial"          # Финансовые
    PERSONNEL = "personnel"          # Кадровые
    LEGAL = "legal"                  # Правовые
    MARKET = "market"                # Рыночные
    REPUTATIONAL = "reputational"    # Репутационные
    IT = "it"                        # ИТ-риски


class RiskPriority(str, enum.Enum):
    LOW = "low"          # Зеленый (1-6)
    MEDIUM = "medium"    # Желтый (7-15)
    HIGH = "high"        # Красный (16-25)


class Risk(Base):
    
    __tablename__ = "risks"
    
    # Основные поля
    id = Column(String(36), primary_key=True, index=True)
    
    title = Column(
        String(500),
        nullable=False,
        comment="Название риска"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Подробное описание риска"
    )
    
    category = Column(
        SQLEnum(RiskCategory),
        nullable=False,
        comment="Категория риска"
    )
    
    # Оценки для матрицы 5x5
    probability = Column(
        Integer,
        default=3,
        nullable=False,
        comment="Вероятность (1-5)"
    )
    
    impact = Column(
        Integer,
        default=3,
        nullable=False,
        comment="Влияние (1-5)"
    )
    
    # Вычисляемый приоритет
    priority = Column(
        SQLEnum(RiskPriority),
        nullable=True,
        comment="Приоритет (вычисляется как P × I)"
    )
    
    # Связь с проектом
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID проекта"
    )
    
    # # Связь с анализом (опционально)
    # analysis_id = Column(
    #     String(36),
    #     ForeignKey("risk_analyses.id", ondelete="SET NULL"),
    #     nullable=True,
    #     comment="ID сессии анализа"
    # )
    
    # Отношения
    project = relationship("Project", back_populates="risks")
    # analysis = relationship("RiskAnalysis", back_populates="risks")
    # solutions = relationship("Solution", back_populates="risk", cascade="all, delete-orphan")
    
    def calculate_priority(self):
        """Вычисляет приоритет на основе вероятности и влияния"""
        score = self.probability * self.impact
        if score <= 6:
            self.priority = RiskPriority.LOW
        elif score <= 15:
            self.priority = RiskPriority.MEDIUM
        else:
            self.priority = RiskPriority.HIGH
    
    def __repr__(self):
        return f"<Risk(id={self.id}, title={self.title}, priority={self.priority})>"