from pydantic import BaseModel


class MassageRequest(BaseModel):
    prompt: str


class GigaChatResponse(BaseModel):
    response: str

class TextChunk(BaseModel):
    context: str
    text: str

class PhilosophyRequest(BaseModel):
    chunks: list[TextChunk]
    question: str

class EvaluateRequest(BaseModel):
    chunks: list[TextChunk]
    question: str
    user_answer: str

class EvaluateResponse(BaseModel):
    score: int
    comment: str