from __future__ import annotations

import html
import re

_MARKDOWN_BOLD = re.compile(r"\*\*(.+?)\*\*")
_MARKDOWN_ITALIC = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_MULTI_SPACE = re.compile(r"[ \t]{2,}")
_MISSING_SPACE = re.compile(r"(?<=[A-Za-zА-Яа-яЁё])(?=[A-ZА-ЯЁ][a-zа-яё])")
_CYRILLIC = re.compile(r"[А-Яа-яЁёІіЇїЄє]")
_LATIN = re.compile(r"[A-Za-z]")
_COMMON_GLUED_WORDS = {
    'Theclaim': 'The claim',
    'Почемупрограммисты': 'Почему программисты',
}


def detect_response_language(text: str, default: str = 'ru') -> str:
    has_cyrillic = bool(_CYRILLIC.search(text))
    has_latin = bool(_LATIN.search(text))
    if has_cyrillic and not has_latin:
        return 'ru'
    if has_latin and not has_cyrillic:
        return 'en'
    return default


def is_identity_question(text: str) -> bool:
    cleaned = ' '.join(text.lower().split())
    patterns = ('who are you', 'what are you', 'what is your name', 'кто ты', 'кто ты такой', 'как тебя зовут', 'что ты такое')
    return any(pattern in cleaned for pattern in patterns)


def identity_answer(language: str) -> str:
    if language == 'en':
        return '<b>CumxAI</b> is the assistant for this chat.'
    return '<b>CumxAI</b> — ассистент этого чата.'


def cleanup_model_text(text: str) -> str:
    cleaned = text.replace('\r\n', '\n').replace('\r', '\n')
    cleaned = cleaned.replace('‑', '-').replace('—', ' — ').replace('–', ' - ')
    cleaned = _MARKDOWN_BOLD.sub(r'\1', cleaned)
    cleaned = _MARKDOWN_ITALIC.sub(r'\1', cleaned)
    cleaned = cleaned.replace('```', '')
    cleaned = _MISSING_SPACE.sub(' ', cleaned)
    for broken, fixed in _COMMON_GLUED_WORDS.items():
        cleaned = cleaned.replace(broken, fixed)
    lines = []
    for line in cleaned.split('\n'):
        normalized = _MULTI_SPACE.sub(' ', line).strip()
        lines.append(normalized)
    cleaned = '\n'.join(lines)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()


def render_pretty_html(text: str) -> str:
    cleaned = cleanup_model_text(text)
    lines = cleaned.split('\n')
    rendered: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            rendered.append('')
            continue
        bullet = False
        if stripped.startswith(('- ', '* ')):
            bullet = True
            stripped = stripped[2:].strip()
        safe = html.escape(stripped)
        if bullet:
            rendered.append(f'• {safe}')
            continue
        if safe.endswith(':') and len(safe) <= 40:
            rendered.append(f'<b>{safe}</b>')
            continue
        rendered.append(safe)
    result = '\n'.join(rendered)
    result = re.sub(r'\n{3,}', '\n\n', result)
    return result.strip()


def truth_template(rendered_html: str, language: str) -> str:
    prefix = '<b>Проверка утверждения</b>\n' if language != 'en' else '<b>Claim analysis</b>\n'
    return prefix + rendered_html


def summary_template(rendered_html: str, language: str) -> str:
    prefix = '<b>Кратко</b>\n' if language != 'en' else '<b>Summary</b>\n'
    return prefix + rendered_html
