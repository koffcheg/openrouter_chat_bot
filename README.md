# openrouter_chat_bot

Telegram AI bot for group chats using aiogram 3 and OpenRouter.

## Phase 1

This phase delivers a runnable MVP with:
- environment-based configuration
- structured logging
- `/help`
- `/ask <text>`
- OpenRouter client wired to the default Nemotron free model
- SQLite-backed chat settings repository bootstrap
- middleware scaffolds for permissions and throttling
- Docker and docker-compose for local/container runs

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
