import json
import os

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src import authorize
from src.models import (
    AskRequest,
    EvaluateRequest,
    EvaluateResponse,
    GigaChatResponse,
)

load_dotenv()

app = FastAPI(title='GigaChat Integration')

KEY = os.getenv('AUTHORIZATION_KEY')
SCOPE = os.getenv('SCOPE')
GIGACHAT_URL = \
    'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'

token = None


@app.get('/')
def root():
    return {'message': 'running...'}


@app.post('/ask', response_model=GigaChatResponse)
def ask(request: AskRequest):
    global token
    if token is None:
        assert SCOPE is not None
        assert KEY is not None
        token = authorize(SCOPE, KEY)

    # ---------- РЕЖИМ 1: обычный ----------
    if not request.philosophy_mode:
        if not request.prompt:
            raise HTTPException(
                400,
                "prompt is required when philosophy_mode=False"
            )

        payload = {
            'model': 'GigaChat',
            'messages': [
                {'role': 'user', 'content': request.prompt}
            ]
        }

    # ---------- РЕЖИМ 2: философия ----------
    else:
        if not request.question or not request.chunks:
            raise HTTPException(
                400,
                "question and chunks are required when philosophy_mode=True"
            )

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
            "Ты — эксперт по философии. " +
            "Используй только предоставленный контекст и текст " +
            "для ответа. Не выходи за рамки источника."
        )

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.request(
        "POST",
        GIGACHAT_URL,
        headers=headers,
        json=payload,
        verify=False
    )

    if response.status_code != 200:
        print(response.text)
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    return GigaChatResponse(response=answer)


@app.post("/evaluate_answer", response_model=EvaluateResponse)
def evaluate_answer(request: EvaluateRequest):
    global token
    if token is None:
        assert SCOPE is not None
        assert KEY is not None
        token = authorize(SCOPE, KEY)

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
1. Оцени ответ по 10-балльной шкале
(0 — полностью неверно, 10 — идеально точно).
2. Дай краткий комментарий, в чём студент прав и где ошибся.

Ответ возвращай строго в JSON формате:
{{
  "score": <целое число>,
  "comment": "<короткое объяснение>"
}}
"""

    system_message = (
            "Ты оцениваешь ответы студентов по философии, " +
            "строго на основе приведённых материалов. " +
            "Не выдумывай новых фактов, не добавляй собственные рассуждения."
    )

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.request(
        "POST",
        GIGACHAT_URL,
        headers=headers,
        json=payload,
        verify=False
    )

    if response.status_code != 200:
        print(response.text)
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    data = response.json()
    answer = data["choices"][0]["message"]["content"]

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


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        '*'
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=80,
        workers=1
    )
