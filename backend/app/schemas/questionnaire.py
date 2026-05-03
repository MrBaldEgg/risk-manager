from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List, Optional


class QuestionResponse(BaseModel):
    """Схема вопроса анкеты"""
    id: str
    text: str
    category: str
    order: int
    is_required: bool
    hint: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class AnswerCreate(BaseModel):
    """Схема для отправки одного ответа"""
    question_id: str
    text: str = Field(..., min_length=1, max_length=2000)


class SubmitRequest(BaseModel):
    """Схема запроса на отправку анкеты"""
    project_id: str
    answers: List[AnswerCreate]


class AnswerResponse(BaseModel):
    """Схема ответа"""
    id: str
    text: str
    question_id: str
    analysis_id: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class AnalysisResponse(BaseModel):
    """Схема результата анализа"""
    id: str
    status: str
    user_id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)