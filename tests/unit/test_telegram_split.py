from bot.utils.telegram_split import split_telegram_text


def test_split_telegram_text_preserves_text_and_limits_chunks():
    text = ('12345\n' * 10)
    chunks = split_telegram_text(text, 12)
    assert ''.join(chunks) == text
    assert all(len(chunk) <= 12 for chunk in chunks)
