from unittest.mock import patch


def test_ask_philosophy(client):
    mock_answer = "Ответ строго по тексту"

    payload = {
        "question": "Что такое философия?",
        "chunks": [
            {
                "context": "Учебник",
                "text": "Философия — это..."
            }
        ]
    }

    with patch("main.call_gigachat", return_value=mock_answer):
        response = client.post("/ask2", json=payload)

    assert response.status_code == 200
    assert response.json()["response"] == mock_answer