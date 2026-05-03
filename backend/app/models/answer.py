from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Answer(Base):
    """Модель ответа пользователя на вопрос анкеты"""
    
    __tablename__ = "answers"
    
    id = Column(String(36), primary_key=True, index=True)
    
    text = Column(
        Text,
        nullable=False,
        comment="Текст ответа (свободная форма)"
    )
    
    analysis_id = Column(
        String(36),
        ForeignKey("risk_analyses.id", ondelete="CASCADE"),
        nullable=False,
        comment="Сессия анализа"
    )
    
    question_id = Column(
        String(36),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        comment="Вопрос анкеты"
    )
    
    # Связи
    analysis = relationship("RiskAnalysis", back_populates="answers")
    question = relationship("Question")
    
    def __repr__(self):
        return f"<Answer(id={self.id}, question_id={self.question_id})>"