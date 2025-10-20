from pydantic import BaseModel


class MassageRequest(BaseModel):
    prompt: str


class GigaChatResponse(BaseModel):
    response: str

class PhilosophyRequest(BaseModel):
    context: list[str]
    text: str
    question: str