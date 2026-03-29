# openrouter_chat_bot

Telegram AI bot for group chats using aiogram 3 and OpenRouter.

## Local run

```bash
cp .env.example .env
# fill BOT_TOKEN and OPENROUTER_API_KEY
python -m venv .venv
. .venv/bin/activate
pip install -e .[dev]
python -m bot.main
```

## Run tests

```bash
pytest -q
```
