import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.question import Question
from app.models.answer import Answer
from app.models.risk_analysis import RiskAnalysis, AnalysisStatus
from app.models.risk import Risk
from app.schemas.questionnaire import (
    QuestionResponse,
    AnswerCreate,
    AnswerResponse,
    SubmitRequest,
    AnalysisResponse,
)
from app.services.risk_generator import risk_generator
from app.api.deps import get_current_active_user

router = APIRouter(prefix="/questionnaire", tags=["questionnaire"])


@router.get("/questions", response_model=List[QuestionResponse])
async def get_questions(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить список вопросов анкеты."""
    result = await db.execute(
        select(Question).order_by(Question.order)
    )
    questions = result.scalars().all()
    return questions


@router.post("/submit", response_model=AnalysisResponse, status_code=status.HTTP_201_CREATED)
async def submit_questionnaire(
    request: SubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Отправить ответы на анкету.
    Создает сессию анализа, сохраняет ответы и генерирует риски.
    """
    # Проверка принадлежности проекта пользователю
    result = await db.execute(
        select(Project).where(
            Project.id == request.project_id,
            Project.owner_id == current_user.id
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    
    # Сессия анализа
    analysis = RiskAnalysis(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        project_id=project.id,
        status=AnalysisStatus.IN_PROGRESS
    )
    db.add(analysis)
    
    # ответы
    answers = []
    for answer_in in request.answers:
        answer = Answer(
            id=str(uuid.uuid4()),
            text=answer_in.text,
            question_id=answer_in.question_id,
            analysis_id=analysis.id
        )
        db.add(answer)
        answers.append(answer)
    
    await db.flush()  
    
    # генерация рисков
    generated_risks = risk_generator.analyze_answers(answers)
    
    # Привязка к проекту
    for risk in generated_risks:
        risk.project_id = project.id
        risk.analysis_id = analysis.id
        db.add(risk)
    
    
    analysis.status = AnalysisStatus.COMPLETED
    
    await db.commit()
    await db.refresh(analysis)
    
    return analysis
