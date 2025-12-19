import os
import json
import uvicorn
import httpx

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import OpenAI

from src import authorize
from src.models import (
    GigaChatResponse,
    MassageRequest,
    PhilosophyRequest,
    EvaluateResponse,
    EvaluateRequest
)

load_dotenv()

KEY = os.getenv("AUTHORIZATION_KEY")
SCOPE = os.getenv("SCOPE")

if not KEY or not SCOPE:
    raise RuntimeError("AUTHORIZATION_KEY or SCOPE not set")

app = FastAPI(title="GigaChat Integration (via OpenAI SDK)")

token: str | None = None
client: OpenAI | None = None

def get_client() -> OpenAI:
    global token, client

    if token is None:
        token = authorize(SCOPE, KEY)

    if client is None:
        http_client = httpx.Client(
            headers={
                "Accept": "application/json",
            },
            verify=False
        )

        client = OpenAI(
            api_key=token,
            base_url="https://gigachat.devices.sberbank.ru/api/v1",
            http_client=http_client
        )

    return client


def call_gigachat(messages: list[dict]) -> str:
    try:
        response = get_client().chat.completions.create(
            model="GigaChat",
            messages=messages,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return response.choices[0].message.content

@app.get("/")
def root():
    return {"message": "running..."}

@app.post("/ask", response_model=GigaChatResponse)
def ask_gigachat(request: MassageRequest):
    messages = [
        {"role": "user", "content": request.prompt}
    ]

    answer = call_gigachat(messages)
    return GigaChatResponse(response=answer)

@app.post("/ask2", response_model=GigaChatResponse)
def ask_philosophy(request: PhilosophyRequest):
    combined_chunks = ""
    for i, chunk in enumerate(request.chunks, start=1):
        combined_chunks += f"""
<chunk {i}>
<context>
{chunk.context}
</context>

<text>
{chunk.text}
</text>
</chunk>
"""

    user_message = f"""
{combined_chunks}

Вопрос пользователя: {request.question}

Отвечай строго по материалу выше, не добавляй собственные рассуждения.
"""

    system_message = (
        "Ты — эксперт по философии. Используй только предоставленный контекст и текст "
        "для ответа. Не выходи за рамки источника."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    answer = call_gigachat(messages)
    return GigaChatResponse(response=answer)

@app.post("/evaluate_answer", response_model=EvaluateResponse)
def evaluate_answer(request: EvaluateRequest):
    combined_chunks = ""
    for i, chunk in enumerate(request.chunks, start=1):
        combined_chunks += f"""
<chunk {i}>
<context>
{chunk.context}
</context>

<text>
{chunk.text}
</text>
</chunk>
"""

    user_message = f"""
Ты — эксперт по философии и преподаватель.

Ниже приведены материалы из учебника:
{combined_chunks}

Вопрос: {request.question}

Ответ студента: {request.user_answer}

Твоя задача:
1. Оцени ответ по 10-балльной шкале (0 — полностью неверно, 10 — идеально точно).
2. Дай краткий комментарий, в чём студент прав и где ошибся.

Ответ возвращай строго в JSON формате:
{{
  "score": <целое число>,
  "comment": "<короткое объяснение>"
}}
"""

    system_message = (
        "Ты оцениваешь ответы студентов по философии, строго на основе приведённых материалов. "
        "Не выдумывай новых фактов, не добавляй собственные рассуждения."
    )

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_message},
    ]

    answer = call_gigachat(messages)

    try:
        parsed = json.loads(answer)
    except json.JSONDecodeError:
        parsed = {
            "score": 0,
            "comment": f"Не удалось распарсить ответ: {answer}"
        }

    if "score" not in parsed or "comment" not in parsed:
        parsed = {
            "score": 0,
            "comment": f"Некорректный формат ответа: {answer}"
        }

    return EvaluateResponse(**parsed)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=80,
        workers=1,
    )