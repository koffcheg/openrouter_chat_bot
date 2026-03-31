from bot.utils.text import cleanup_model_text, detect_response_language, identity_answer, is_identity_question, render_pretty_html


def test_cleanup_model_text_removes_markdown_and_normalizes_spacing():
    raw = "**Hello**  world\n\n\nTheclaim is *fine*.\nПочемупрограммисты"
    cleaned = cleanup_model_text(raw)
    assert '**' not in cleaned
    assert '*fine*' not in cleaned
    assert 'Hello world' in cleaned
    assert 'The claim is fine.' in cleaned
    assert 'Почему программисты' in cleaned


def test_identity_helpers_and_language_detection():
    assert detect_response_language('Привет, кто ты?') == 'ru'
    assert detect_response_language('who are you?') == 'en'
    assert is_identity_question('who are you?') is True
    assert is_identity_question('Привет, кто ты?') is True
    assert '<b>CumxAI</b>' in identity_answer('ru')
    assert '<b>CumxAI</b>' in identity_answer('en')


def test_render_pretty_html_formats_sections_and_bullets():
    raw = "Assessment:\n- first point\n- second point\n\n**Plain** line"
    rendered = render_pretty_html(raw)
    assert '<b>Assessment:</b>' in rendered
    assert '• first point' in rendered
    assert '• second point' in rendered
    assert 'Plain line' in rendered
