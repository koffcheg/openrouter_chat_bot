from bot.services.ai.output_validator import build_repair_prompt, validate_output


def test_validate_output_rejects_han_script_for_cyrillic_language():
    result = validate_output(text='У presently нет科学依据 для этого.', language='uk', command='ask')
    assert result.is_valid is False
    assert result.reason == 'unexpected_han_script'


def test_validate_output_rejects_mixed_script_token():
    result = validate_output(text='Це bреgeri виглядає дивно.', language='uk', command='ask')
    assert result.is_valid is False
    assert result.reason == 'mixed_script_token'


def test_validate_output_rejects_wrong_truth_heading_language():
    text = 'Assessment:\ntext\nKnown facts:\n- one\nUncertainty:\n- two\nWhat would need live verification:\n- three'
    result = validate_output(text=text, language='ru', command='truth')
    assert result.is_valid is False
    assert result.reason == 'wrong_truth_titles_language'


def test_validate_output_accepts_clean_truth_with_localized_titles():
    text = 'Оцінка:\nТекст\nВідомі факти:\n- факт\nНевизначеність:\n- пункт\nЩо потребувало б живої перевірки:\n- ще пункт'
    result = validate_output(text=text, language='uk', command='truth')
    assert result.is_valid is True


def test_build_repair_prompt_mentions_preserving_truth_titles():
    prompt = build_repair_prompt(text='bad', language='ru', command='truth')
    assert 'Russian' in prompt
    assert 'Оценка' in prompt
    assert 'Что потребовало бы живой проверки' in prompt
