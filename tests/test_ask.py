from unittest.mock import patch


def test_ask_gigachat(client):
    mock_answer = "Привет, я GigaChat"

    with patch("main.call_gigachat", return_value=mock_answer):
        response = client.post(
            "/ask",
            json={"prompt": "Привет"}
        )

    assert response.status_code == 200
    assert response.json() == {"response": mock_answer}