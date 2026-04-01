from __future__ import annotations

import re
from dataclasses import dataclass

from bot.services.ai.prompt_policies import normalize_language_code, truth_section_titles

_LATIN_WORD = re.compile(r"\b[A-Za-z]{3,}\b")
_CYRILLIC_WORD = re.compile(r"\b[А-Яа-яЁёІіЇїЄє]{3,}\b")
_MIXED_TOKEN = re.compile(r"(?=.*[A-Za-z])(?=.*[А-Яа-яЁёІіЇїЄє])[A-Za-zА-Яа-яЁёІіЇїЄє]{4,}")
_HAN = re.compile(r"[\u4e00-\u9fff]")


@dataclass(frozen=True, slots=True)
class OutputValidationResult:
    is_valid: bool
    reason: str = ''


def validate_output(*, text: str, language: str, command: str) -> OutputValidationResult:
    normalized_language = normalize_language_code(language)
    candidate = text.strip()
    if not candidate:
        return OutputValidationResult(False, 'empty_output')
    if _HAN.search(candidate):
        return OutputValidationResult(False, 'unexpected_han_script')
    if _MIXED_TOKEN.search(candidate):
        return OutputValidationResult(False, 'mixed_script_token')

    latin_words = len(_LATIN_WORD.findall(candidate))
    cyrillic_words = len(_CYRILLIC_WORD.findall(candidate))

    if normalized_language in {'ru', 'uk'} and latin_words >= 6 and latin_words > cyrillic_words // 2:
        return OutputValidationResult(False, 'too_many_latin_words')
    if normalized_language == 'en' and cyrillic_words >= 4 and cyrillic_words > latin_words // 2:
        return OutputValidationResult(False, 'too_many_cyrillic_words')

    if command == 'truth':
        missing_titles = [title for title in truth_section_titles(normalized_language) if title not in candidate]
        if missing_titles:
            return OutputValidationResult(False, 'missing_truth_titles')

    return OutputValidationResult(True)


def build_repair_prompt(*, text: str, language: str, command: str) -> str:
    normalized_language = normalize_language_code(language)
    language_name = {'ru': 'Russian', 'uk': 'Ukrainian', 'en': 'English'}.get(normalized_language, 'Russian')
    extra = ''
    if command == 'truth':
        titles = ', '.join(truth_section_titles(normalized_language))
        extra = f' Preserve exactly these section headings: {titles}.'
    return (
        f'Rewrite the answer below in clean {language_name} only. '
        'Keep the meaning, remove mixed-language fragments, remove malformed words, and keep the answer natural and readable.'
        f'{extra}\n\n'
        f'Answer to rewrite:\n{text.strip()}'
    )
