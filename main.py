import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src import (
    context_responce,
    evaluate_responce,
    parse_evaluate_res,
    reduce_responce,
    simple_responce,
)
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
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


@app.get('/')
def root():
    return {'message': 'running...'}


@app.post('/ask', response_model=GigaChatResponse)
def ask(request: AskRequest):
    global token

    func = simple_responce
    payload = {}

    # ---------- РЕЖИМ 1: обычный ----------
    if not request.philosophy_mode:
        if not request.prompt:
            raise HTTPException(
                400,
                "prompt is required when philosophy_mode=False"
            )
        payload = {'prompt': request.prompt}

    # ---------- РЕЖИМ 2: философия ----------
    else:
        if not request.question or not request.chunks:
            raise HTTPException(
                400,
                "question and chunks are required when philosophy_mode=True"
            )
        func = context_responce
        payload = {
            'question': request.question,
            'chunks': request.chunks
        }
    
    token, answer = reduce_responce(
        func,
        token,
        GIGACHAT_URL,
        KEY,
        SCOPE,
        headers,
        **payload
    )

    return GigaChatResponse(response=answer)


@app.post("/evaluate_answer", response_model=EvaluateResponse)
def evaluate_answer(request: EvaluateRequest):
    global token

    token, answer = reduce_responce(
        evaluate_responce,
        token,
        GIGACHAT_URL,
        KEY,
        SCOPE,
        headers,
        question=request.question,
        user_answer=request.user_answer,
        chunks=request.chunks,
    )

    return EvaluateResponse(**parse_evaluate_res(answer))


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
