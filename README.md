# openrouter_chat_bot

Telegram AI bot for group chats using aiogram 3 and OpenRouter.

## Features

CumxAI supports:
- `/ask` for normal questions
- `/truth` for internal-knowledge claim analysis
- `/sum` for summaries
- `/fun` for playful replies
- reply-based command usage
- per-chat language and style settings
- admin model selection and runtime status
- automatic Telegram command menu registration on startup

This bot is designed for a free-tier setup first. It does not provide live web verification by default.

## Public commands

- `/start` — welcome message
- `/help` — command reference
- `/about` — short bot description
- `/ask [text]` — ask a question
- `/truth` — reply to a message to analyze a claim
- `/sum` — reply to a message to summarize it
- `/fun [text]` — playful answer mode

## Admin commands

- `/status` — runtime status and observability
- `/models` — list available models
- `/setmodel &lt;slug&gt;` — set current model
- `/pause` — pause replies in the current chat
- `/resume` — resume replies in the current chat
- `/setlang auto|ru|ua|en` — set reply language
- `/setstyle pretty|concise|playful` — set response style
- `/viewsettings` — show current chat settings
- `/resetsettings` — reset language/style to defaults

## Reply-based usage

- reply with `/ask` to respond based on that message
- reply with `/truth` to analyze that message as a claim
- reply with `/sum` to summarize that message
- reply with `/fun` to make a playful reply to that message

## Language behavior

User-facing language options are:
- `auto`
- `ru`
- `ua`
- `en`

Notes:
- user-facing Ukrainian is shown as `ua`
- Telegram command localization uses the official Telegram language code internally
- in `auto` mode, public UI falls back to Russian when the language is unclear

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

## Required environment values

At minimum, configure:
- `BOT_TOKEN`
- `OPENROUTER_API_KEY`

Also review `.env.example` for the rest of the runtime settings.

## Backup

A simple SQLite backup helper is available at `scripts/backup_db.sh`.

```bash
./scripts/backup_db.sh
```

## Troubleshooting

- If `/help` formatting breaks, check Telegram HTML escaping in user-visible text.
- If the command menu does not refresh immediately, restart the bot and wait for Telegram client cache refresh.
- If the provider returns an invalid response, the bot should now show a user-facing provider error instead of crashing the command path.
- Typing indicators may be brief in some Telegram clients when responses are fast.

## Pilot checklist

Before inviting users:
- run `pytest -q`
- start the bot locally
- verify `/start`, `/help`, `/about`
- verify `/ask`, `/truth`, `/sum`, `/fun`
- verify `/setlang ua`, `/setstyle pretty`, `/viewsettings`, `/resetsettings`
- verify `/status`
- verify threaded replies
- verify command menu updates after restart

## Current limitations

- `/truth` is internal-knowledge analysis, not live browsing
- free-tier model behavior can still vary
- command names remain Latin-format due to Telegram constraints
