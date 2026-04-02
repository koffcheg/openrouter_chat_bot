from bot.services.ai.prompt_policies import command_policy_text, normalize_language_code, normalize_summary_output, normalize_truth_sections, truth_section_titles


def test_normalize_language_code_maps_ua_to_uk():
    assert normalize_language_code('ua') == 'uk'
    assert normalize_language_code('uk') == 'uk'
    assert normalize_language_code('en') == 'en'


def test_truth_section_titles_are_localized():
    assert truth_section_titles('en')[0] == 'Assessment'
    assert truth_section_titles('uk')[0] == 'Оцінка'
    assert truth_section_titles('ru')[0] == 'Оценка'


def test_command_policy_text_mentions_single_language_for_truth():
    policy = command_policy_text('truth', 'uk')
    assert 'Reply in exactly one language' in policy
    assert 'Оцінка' in policy
    assert 'Відомі факти' in policy


def test_normalize_truth_sections_rewrites_headings():
    text = 'Assessment\ntext\nKnown facts:\n- one\nUncertainty\nmaybe\nWhat would need live verification\nmore'
    normalized = normalize_truth_sections(text, 'ru')
    assert 'Оценка:' in normalized
    assert 'Известные факты:' in normalized
    assert 'Неопределённость:' in normalized
    assert 'Что потребовало бы живой проверки:' in normalized


def test_normalize_summary_output_strips_duplicate_summary_titles():
    text = 'Summary\nShort summary\n• one\n• two'
    normalized = normalize_summary_output(text, 'en')
    assert normalized == '• one\n• two'
