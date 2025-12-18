from pydantic import BaseModel


class MassageRequest(BaseModel):
    prompt: str


class GigaChatResponse(BaseModel):
    response: str