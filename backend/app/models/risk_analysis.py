from sqlalchemy import Column, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.base import Base
import enum


class AnalysisStatus(str, enum.Enum):
    """Статусы анализа"""
    IN_PROGRESS = "in_progress"  # Анкета заполняется
    COMPLETED = "completed"      # Анализ завершен
    FAILED = "failed"            # Ошибка анализа


class RiskAnalysis(Base):
    """Модель сессии анализа рисков"""
    
    __tablename__ = "risk_analyses"
    
    id = Column(String(36), primary_key=True, index=True)
    
    user_id = Column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="Пользователь, проходящий анализ"
    )
    
    project_id = Column(
        String(36),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        comment="Проект для анализа"
    )
    
    status = Column(
        SQLEnum(AnalysisStatus),
        default=AnalysisStatus.IN_PROGRESS,
        nullable=False,
        comment="Статус анализа"
    )
    
    # Связи
    user = relationship("User", back_populates="analyses")
    project = relationship("Project", back_populates="analyses")
    answers = relationship("Answer", back_populates="analysis", cascade="all, delete-orphan")
    risks = relationship("Risk", back_populates="analysis")
    
    def __repr__(self):
        return f"<RiskAnalysis(id={self.id}, status={self.status})>"