from pydantic import BaseModel
from typing import List

class MassageRequest(BaseModel):
    prompt: str


class GigaChatResponse(BaseModel):
    response: str

class TextChunk(BaseModel):
    context: str
    text: str

class PhilosophyRequest(BaseModel):
    chunks: List[TextChunk]
    question: str

class EvaluateRequest(BaseModel):
    chunks: List[TextChunk]
    question: str
    user_answer: str

class EvaluateResponse(BaseModel):
    score: int
    comment: str