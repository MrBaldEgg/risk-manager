from sqlalchemy import Column, String, Text, Integer, Boolean, Enum as SQLEnum
from app.db.base import Base
import enum


class QuestionCategory(str, enum.Enum):
    """Категории вопросов"""
    SWOT_STRENGTH = "swot_strength"       # Сильные стороны
    SWOT_WEAKNESS = "swot_weakness"       # Слабые стороны
    SWOT_OPPORTUNITY = "swot_opportunity" # Возможности
    SWOT_THREAT = "swot_threat"           # Угрозы
    PEST_POLITICAL = "pest_political"     # Политические факторы
    PEST_ECONOMIC = "pest_economic"       # Экономические факторы
    PEST_SOCIAL = "pest_social"           # Социальные факторы
    PEST_TECHNOLOGICAL = "pest_technological"  # Технологические факторы
    FREE_FORM = "free_form"              # Свободный ответ


class Question(Base):
    """Модель вопроса анкеты"""
    
    __tablename__ = "questions"
    
    id = Column(String(36), primary_key=True, index=True)
    
    text = Column(
        Text,
        nullable=False,
        comment="Текст вопроса"
    )
    
    category = Column(
        SQLEnum(QuestionCategory),
        nullable=False,
        comment="Категория вопроса (SWOT/PEST/свободный)"
    )
    
    order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Порядок отображения"
    )
    
    is_required = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Обязательный ли вопрос"
    )
    
    hint = Column(
        Text,
        nullable=True,
        comment="Подсказка к вопросу"
    )
    
    def __repr__(self):
        return f"<Question(id={self.id}, category={self.category}, order={self.order})>"