
from pydantic import BaseModel


class GigaChatResponse(BaseModel):
    response: str


class TextChunk(BaseModel):
    context: str
    text: str


class AskRequest(BaseModel):
    prompt: str | None = None           # для обычного ask
    question: str | None = None         # для философского режима
    chunks: list[TextChunk] | None = None   # для философского режима
    philosophy_mode: bool = False          # флаг переключения


class EvaluateRequest(BaseModel):
    chunks: list[TextChunk]
    question: str
    user_answer: str


class EvaluateResponse(BaseModel):
    score: int
    comment: str