DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful AI assistant for a Telegram group. "
    "Answer clearly, safely, and concisely."
)
START_TEXT = """Hi. I am CumxAI, a Telegram assistant for this chat.

Use /help to see the available commands.
Admins can also use /status, /models, /setmodel, /pause, and /resume."""
HELP_TEXT = """Available commands:
/start — show a short welcome message
/help — show this help
/ask [text] — ask the assistant a question
/truth — reply to a message to analyze the claim
/sum — reply to a message to summarize it
/fun [text] — playful answer mode"""
DEFAULT_CHAT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
