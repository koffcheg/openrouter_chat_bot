from bot.config.settings import Settings


def test_blank_telegram_parse_mode_falls_back_to_html():
    settings = Settings.model_validate({
        'BOT_TOKEN': 'x',
        'OPENROUTER_API_KEY': 'y',
        'TELEGRAM_PARSE_MODE': '',
    })
    assert settings.telegram_parse_mode == 'HTML'
