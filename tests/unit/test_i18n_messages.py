from bot.i18n.messages import resolve_reply_language, text


def test_resolve_reply_language_prefers_explicit_setting():
    assert resolve_reply_language('ua', 'en') == 'uk'
    assert resolve_reply_language('ru', 'en') == 'ru'


def test_resolve_reply_language_falls_back_to_detected():
    assert resolve_reply_language('auto', 'en') == 'en'
    assert resolve_reply_language('auto', 'ua') == 'uk'


def test_text_localizes_provider_timeout():
    assert text('provider_timeout', 'en').startswith('The AI provider timed out.')
    assert text('provider_timeout', 'ru').startswith('AI-провайдер')
    assert text('provider_timeout', 'ua').startswith('AI-провайдер')


def test_text_formats_cooldown_seconds():
    assert '7' in text('cooldown', 'en', seconds=7)
    assert '7' in text('cooldown', 'ru', seconds=7)
