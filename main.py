import os
import requests
from src import authorize
from src.models import GigaChatResponse, MassageRequest, PhilosophyRequest
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title='GigaChat Integration')

KEY = os.getenv('AUTHORIZATION_KEY')
SCOPE = os.getenv('SCOPE')
GIGACHAT_URL = 'https://gigachat.devices.sberbank.ru/api/v1/chat/completions'

token = None

@app.get('/')
def root():
    return {'message': 'running...'}


@app.post('/ask', response_model=GigaChatResponse)
def ask_gigachat(request: MassageRequest):
    global token
    if token is None:
        assert SCOPE is not None
        assert KEY is not None
        token = authorize(SCOPE, KEY)

    payload = {
        'model': 'GigaChat',
        'messages': [
            {
                'role': 'user',
                'content': request.prompt
            }
        ]
    }
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    response = requests.request(
        'POST',
        GIGACHAT_URL,
        headers=headers,
        json=payload,
        verify=False
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    answer = data['choices'][0]['message']['content']
    return GigaChatResponse(response=answer)


@app.post("/ask2", response_model=GigaChatResponse)
def ask_philosophy(request: PhilosophyRequest):
    global token
    if token is None:
        assert SCOPE is not None
        assert KEY is not None
        token = authorize(SCOPE, KEY)

    joined_context = "\n\n".join(request.context)

    user_message = f"""
<context>
{joined_context}
</context>

<text>
{request.text}
</text>

Вопрос пользователя: {request.question}

Отвечай строго по материалу выше, не добавляй собственные рассуждения.
"""

    system_message = "Ты — эксперт по философии. Используй только предоставленный контекст и текст " + "для ответа. Не выходи за рамки источника."


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
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    answer = data["choices"][0]["message"]["content"]
    return GigaChatResponse(response=answer)
