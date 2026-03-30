# openrouter_chat_bot

Telegram AI bot for group chats using aiogram 3 and OpenRouter.

## Local run

```bash
cp .env.example .env
# fill BOT_TOKEN and OPENROUTER_API_KEY
python -m venv .venv
. .venv/bin/activate
pip install .[dev]
python -m bot.main
```

## Run tests

```bash
pytest -q
```

## Backup the SQLite database

The runtime database path is taken from `SQLITE_PATH`.
A simple host-side backup helper is available at `scripts/backup_db.sh`.
Run it from the repository root while the bot is stopped if you want the safest copy.
