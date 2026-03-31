from bot.utils.text import cleanup_model_text


def test_cleanup_model_text_removes_markdown_and_normalizes_spacing():
    raw = "**Hello**  world\n\n\nTheclaim is *fine*.\nПочемупрограммисты"
    cleaned = cleanup_model_text(raw)
    assert '**' not in cleaned
    assert '*fine*' not in cleaned
    assert 'Hello world' in cleaned
    assert 'The claim is fine.' in cleaned
    assert 'Почему программисты' in cleaned
