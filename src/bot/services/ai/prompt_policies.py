from __future__ import annotations

import re


def normalize_language_code(language: str | None, fallback: str = 'ru') -> str:
    normalized = (language or '').strip().lower()
    mapping = {
        'ua': 'uk',
        'uk': 'uk',
        'ru': 'ru',
        'en': 'en',
        'auto': 'auto',
    }
    return mapping.get(normalized, fallback)


def truth_section_titles(language: str) -> tuple[str, str, str, str]:
    normalized = normalize_language_code(language)
    if normalized == 'en':
        return ('Assessment', 'Known facts', 'Uncertainty', 'What would need live verification')
    if normalized == 'uk':
        return ('Оцінка', 'Відомі факти', 'Невизначеність', 'Що потребувало б живої перевірки')
    return ('Оценка', 'Известные факты', 'Неопределённость', 'Что потребовало бы живой проверки')


def summary_heading_titles(language: str) -> tuple[str, ...]:
    normalized = normalize_language_code(language)
    if normalized == 'en':
        return ('Summary', 'Short summary', 'Brief summary')
    if normalized == 'uk':
        return ('Коротко', 'Коротке резюме', 'Стислий підсумок')
    return ('Кратко', 'Краткое резюме', 'Короткий итог')


def command_policy_text(command: str, language: str) -> str:
    normalized = normalize_language_code(language)
    language_name = {'ru': 'Russian', 'uk': 'Ukrainian', 'en': 'English'}.get(normalized, 'Russian')
    if command == 'ask':
        return (
            f'Reply in exactly one language: {language_name}. '
            'Answer directly. Keep the default answer short and useful. '
            'If the request is vague, ask one brief clarifying question instead of inventing details.'
        )
    if command == 'sum':
        return (
            f'Reply in exactly one language: {language_name}. '
            'Summarize only the provided text. Do not add new facts. '
            'Keep the result compact and avoid duplicate headings or repeated framing.'
        )
    if command == 'fun':
        return (
            f'Reply in exactly one language: {language_name}. '
            'Keep humor short, clear, and punchy. Prefer one compact joke over a long explanation.'
        )
    if command == 'truth':
        assessment, known_facts, uncertainty, live_check = truth_section_titles(normalized)
        return (
            f'Reply in exactly one language: {language_name}. '
            'Do not claim to have performed live verification. '
            'Use exactly four sections with these headings and no others: '
            f'{assessment}, {known_facts}, {uncertainty}, {live_check}. '
            'Separate known facts from hypotheses clearly and state uncertainty when evidence is limited.'
        )
    return f'Reply in exactly one language: {language_name}. Keep the answer clear and concise.'


def normalize_truth_sections(text: str, language: str) -> str:
    canonical_titles = truth_section_titles(language)
    alias_map = {
        'assessment': canonical_titles[0],
        'known facts': canonical_titles[1],
        'uncertainty': canonical_titles[2],
        'what would need live verification': canonical_titles[3],
        'оценка': canonical_titles[0],
        'известные факты': canonical_titles[1],
        'неопределенность': canonical_titles[2],
        'неопределённость': canonical_titles[2],
        'что потребовало бы живой проверки': canonical_titles[3],
        'оцінка': canonical_titles[0],
        'відомі факти': canonical_titles[1],
        'невизначеність': canonical_titles[2],
        'що потребувало б живої перевірки': canonical_titles[3],
    }
    lines: list[str] = []
    for raw_line in text.split('\n'):
        stripped = raw_line.strip()
        normalized = re.sub(r'[:：]\s*$', '', stripped).strip().lower()
        replacement = alias_map.get(normalized)
        if replacement is not None:
            lines.append(f'{replacement}:')
        else:
            lines.append(raw_line)
    return '\n'.join(lines)


def normalize_summary_output(text: str, language: str) -> str:
    titles = {title.lower() for title in summary_heading_titles(language)}
    lines = [line for line in text.split('\n')]
    cleaned: list[str] = []
    skipped_heading = 0
    for line in lines:
        stripped = re.sub(r'[:：]\s*$', '', line.strip()).lower()
        if skipped_heading < 2 and stripped in titles:
            skipped_heading += 1
            continue
        cleaned.append(line)
    result = '\n'.join(cleaned).strip()
    return result
