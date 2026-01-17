import json
import os
import uuid
from contextlib import asynccontextmanager

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException

from src import authorize
from src.models import (
    EvaluateRequest,
    EvaluateResponse,
    GigaChatResponse,
    AskRequest,
)
from src.server.Infrastructure import create_tables
from src.server.Schemas import (
    SCard,
    SCardCreate,
    SGameProgress,
    SGameProgressCreateDto,
    SLevel,
    SLevelCreate,
)
from src.server.Services import (
    CardService,
    GameProgressService,
    LevelService,
    get_card_service,
    get_game_progress_service,
    get_level_service,
)

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    print("База готова")
    yield

app = FastAPI(title='GigaChat Integration',
              lifespan=lifespan)

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
            raise HTTPException(400, "prompt is required when philosophy_mode=False")

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


@app.post("/card",
          response_model=SCard,
          tags=['Card'])
async def post_card(
    card_data: SCardCreate,
    card_service: CardService | None = None
):
    if card_service is None:
        card_service = Depends(get_card_service)
    assert card_service is not None

    return await card_service.create_card(card_data)


@app.get("/card",
         response_model=SCard,
         tags=['Card'])
async def get_card(
    card_id: uuid.UUID,
    card_service: CardService | None = None
):
    if card_service is None:
        card_service = Depends(get_card_service)
    assert card_service is not None

    return await card_service.get_card_by_id(card_id)


@app.get("/card/all",
         response_model=list[SCard],
         tags=['Card'])
async def get_all_cards(
    card_service: CardService | None = None
):
    if card_service is None:
        card_service = Depends(get_card_service)
    assert card_service is not None

    return await card_service.get_all_cards()


@app.delete("/card",
            tags=['Card'])
async def delete_card(
    card_id: uuid.UUID,
    card_service: CardService | None = None
):
    if card_service is None:
        card_service = Depends(get_card_service)
    assert card_service is not None

    await card_service.delete_card(card_id)


@app.post("/level",
          response_model=SLevel,
          tags=['Level'])
async def post_level(
    level_data: SLevelCreate,
    level_service: LevelService | None = None
):
    if level_service is None:
        level_service = Depends(get_level_service)
    assert level_service is not None

    return await level_service.create_level(level_data)


@app.get("/level",
         response_model=SLevel,
         tags=['Level'])
async def get_level(
    level_id: uuid.UUID,
    level_service: LevelService | None = None
):
    if level_service is None:
        level_service = Depends(get_level_service)
    assert level_service is not None

    return await level_service.get_level_by_id(level_id)


@app.get("/level/all",
         response_model=list[SLevel],
         tags=['Level'])
async def get_all_levels(
    level_service: LevelService | None = None
):
    if level_service is None:
        level_service = Depends(get_level_service)
    assert level_service is not None

    return await level_service.get_all_levels()


@app.delete("/level",
            tags=['Level'])
async def delete_level(
    level_id: uuid.UUID,
    level_service: LevelService | None = None
):
    if level_service is None:
        level_service = Depends(get_level_service)
    assert level_service is not None

    await level_service.delete_level(level_id)


@app.post("/game",
          response_model=SGameProgress,
          tags=['Game'])
async def start_game(
    game_prog: SGameProgressCreateDto,
    game_prog_service: GameProgressService | None = None
):
    if game_prog_service is None:
        game_prog_service = Depends(get_game_progress_service)
    assert game_prog_service is not None

    return await game_prog_service.create_game_progress(game_prog)


@app.get("/game",
         response_model=SGameProgress,
         tags=['Game'])
async def get_game(
    game_prog_id: uuid.UUID,
    game_prog_service: GameProgressService | None = None
):
    if game_prog_service is None:
        game_prog_service = Depends(get_game_progress_service)
    assert game_prog_service is not None

    return await (game_prog_service
                  .get_game_progress_by_id(game_prog_id))


@app.get("/game/all",
         response_model=list[SGameProgress],
         tags=['Game'])
async def get_all_games(
    game_prog_service: GameProgressService | None = None
):
    if game_prog_service is None:
        game_prog_service = Depends(get_game_progress_service)
    assert game_prog_service is not None

    return await game_prog_service.get_all_game_progresses()


@app.delete("/game",
            tags=['Game'])
async def delete_game(
    game_prog_id: uuid.UUID,
    game_prog_service: GameProgressService | None = None
):
    if game_prog_service is None:
        game_prog_service = Depends(get_game_progress_service)
    assert game_prog_service is not None

    await game_prog_service.delete_game_progress(game_prog_id)


@app.patch("/game",
           tags=['Game'])
async def make_move(
    game_prog_id: uuid.UUID,
    choice: int,
    game_prog_service: GameProgressService | None = None
):
    if game_prog_service is None:
        game_prog_service = Depends(get_game_progress_service)
    assert game_prog_service is not None

    return await game_prog_service.make_move(game_prog_id, choice)


if __name__ == '__main__':
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=80,
        workers=1
    )
