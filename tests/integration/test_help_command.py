from bot.core.constants import HELP_TEXT


def test_help_text_contains_phase3_commands() -> None:
    assert '/start' in HELP_TEXT
    assert '/help' in HELP_TEXT
    assert '/truth' in HELP_TEXT
    assert '/sum' in HELP_TEXT
    assert '/fun [text]' in HELP_TEXT
