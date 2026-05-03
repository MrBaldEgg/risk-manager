from fastapi import APIRouter
from app.api.v1.endpoints import auth, projects, risks, questionnaire

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(projects.router)
api_router.include_router(risks.router)
api_router.include_router(questionnaire.router)