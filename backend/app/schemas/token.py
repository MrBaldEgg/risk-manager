from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Схема данных внутри JWT токена"""
    sub: Optional[str] = None  # subject (user_id)
    exp: Optional[int] = None  # expiration time