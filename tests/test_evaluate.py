from unittest.mock import patch


def test_evaluate_answer_success(client):
    mock_llm_response = """
    {
        "score": 8,
        "comment": "Ответ в целом верный"
    }
    """

    payload = {
        "question": "Что такое философия?",
        "user_answer": "Это наука о мышлении",
        "chunks": [
            {
                "context": "Учебник",
                "text": "Философия — дисциплина..."
            }
        ]
    }

    with patch("main.call_gigachat", return_value=mock_llm_response):
        response = client.post("/evaluate_answer", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["score"] == 8
    assert "верный" in data["comment"]
