from collections.abc import Callable
from typing import Any

import requests

from src.models import TextChunk

from .autorization import authorize
from .utils import combine_chunks, get_giga_content


def simple_responce(
    url: str,
    headers: dict[str, str],
    prompt: str
) -> requests.Response:
    payload = {
        'model': 'GigaChat',
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }

    return requests.request(
        "POST",
        url,
        headers=headers,
        json=payload,
        verify=False
    )


def context_responce(
    url: str,
    headers: dict[str, str],
    question: str,
    chunks: list[TextChunk]
) -> requests.Response:
    system_message = f'Ты — эксперт по философии. \
        Используй только предоставленный контекст и текст для ответа. \
        Не выходи за рамки источника. Ниже приведены материалы из учебника:\
        \n{combine_chunks(chunks)}'
    user_message = f'Вопрос пользователя: {question}\n\
        Отвечай строго по материалу выше, не добавляй собственные рассуждения.'
    
    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    return requests.request(
        "POST",
        url,
        headers=headers,
        json=payload,
        verify=False
    )


def evaluate_responce(
    url: str,
    headers: dict[str, str],
    question: str,
    user_answer: str,
    chunks: list[TextChunk]
) -> requests.Response:
    system_message = f'Ты — эксперт по философии. \
        Используй только предоставленный контекст и текст для ответа. \
        Не выходи за рамки источника. Ниже приведены материалы из учебника:\
        \n{combine_chunks(chunks)}\
        \nТвоя задача:\
        \n1. Оцени ответ по 10-балльной шкале\
        \n(0 — полностью неверно, 10 — идеально точно).\
        \n2. Дай краткий комментарий, в чём студент прав и где ошибся.\
        \nОтвет возвращай строго в JSON формате:\
        \n{{\
        \n"score": <целое число>,\
        \n"comment": "<короткое объяснение>"\
        \n}}'
    user_message = f'Вопрос: {question}\
        \nОтвет студента: {user_answer}'
    
    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
    }

    return requests.request(
        "POST",
        url,
        headers=headers,
        json=payload,
        verify=False
    )


def reduce_responce(
    func: Callable[..., requests.Response],
    token: str | None,
    url: str,
    key: str | None,
    scope: str | None,
    headers: dict[str, str], 
    **payload
) -> tuple[str, Any]:
    if token is None:
        assert scope is not None
        assert key is not None
        token = authorize(scope, key)

    headers = {
        **headers,
        "Authorization": f"Bearer {token}"
    }
    res = func(url=url, headers=headers, **payload)

    if res.status_code == 401:
        assert scope is not None
        assert key is not None
        token = authorize(scope, key)
        res = func(url=url, headers=headers, **payload)
    
    return token, get_giga_content(res)
