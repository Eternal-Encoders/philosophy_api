# Апи для использования GigaChat'а

## Начало работы

**Создание .env**

В корне проекта необходимо создать файл .env с подобным содержанием
```
AUTHORIZATION_KEY="Токен авторизации в Гигачат"
SCOPE="GIGACHAT_API_PERS"
```

### Стандартный Python

Создаем виртуальное окружение и  активируем его
```bash
python -m venv .venv
.venv/Scripts/activate
```

Устанавливаем библиотеки
```bash
pip install -r requirements.txt
```

Запускаем
```bash
python -m fastapi dev main.py
```
### UV

Устанавливаем библиотеки
```bash
uv venv
uv sync
```

Запускаем
```bash
uv run fastapi dev main.py
```