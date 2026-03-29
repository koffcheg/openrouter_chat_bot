from bot.core.constants import HELP_TEXT


def test_help_text_contains_phase1_commands() -> None:
    assert "/help" in HELP_TEXT
    assert "/ask <text>" in HELP_TEXT
