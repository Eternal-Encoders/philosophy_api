import json
from typing import Any

import requests
from fastapi import HTTPException

from .models import TextChunk


def combine_chunks(chunks: list[TextChunk]) -> str:
    res = ''
    for i, chunk in enumerate(chunks, start=1):
        res += f'<chunk {i}>\n<context>\n{chunk.context}\n</context>\n<text>\
            \n{chunk.text}\n</text>\n</chunk>\n'
    return res


def get_giga_content(res: requests.Response):
    if res.status_code != 200:
        print(res.text)
        raise HTTPException(
            status_code=res.status_code,
            detail=res.text
        )

    data = res.json()
    return data["choices"][0]["message"]["content"]


def parse_evaluate_res(answer: str) -> dict[str, Any]:
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
    
    return parsed