from pydantic import BaseModel
from typing import List, Optional


class GigaChatResponse(BaseModel):
    response: str


class TextChunk(BaseModel):
    context: str
    text: str


class AskRequest(BaseModel):
    prompt: Optional[str] = None           # для обычного ask
    question: Optional[str] = None         # для философского режима
    chunks: Optional[List[TextChunk]] = None   # для философского режима
    philosophy_mode: bool = False          # флаг переключения


class EvaluateRequest(BaseModel):
    chunks: List[TextChunk]
    question: str
    user_answer: str


class EvaluateResponse(BaseModel):
    score: int
    comment: str