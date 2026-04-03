from __future__ import annotations


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


def resolve_reply_language(preferred_language: str | None, detected_language: str = 'ru') -> str:
    preferred = normalize_language_code(preferred_language)
    if preferred != 'auto':
        return preferred
    return normalize_language_code(detected_language, fallback='ru')


_MESSAGES = {
    'paused': {
        'en': 'This chat is currently paused by an admin.',
        'ru': 'Этот чат сейчас поставлен на паузу администратором.',
        'uk': 'Цей чат зараз поставлений на паузу адміністратором.',
    },
    'cooldown': {
        'en': 'Cooldown active. Please wait {seconds} seconds before sending another request.',
        'ru': 'Сейчас действует кулдаун. Подождите {seconds} сек. перед следующим запросом.',
        'uk': 'Зараз діє кулдаун. Зачекайте {seconds} с перед наступним запитом.',
    },
    'active_request': {
        'en': 'You already have an active request in progress.',
        'ru': 'У вас уже есть активный запрос в обработке.',
        'uk': 'У вас уже є активний запит в обробці.',
    },
    'ask_need_text': {
        'en': 'Please provide text for this command.',
        'ru': 'Пожалуйста, добавьте текст к этой команде.',
        'uk': 'Будь ласка, додайте текст до цієї команди.',
    },
    'ask_too_long': {
        'en': 'Input is too long. Maximum length is {max_chars} characters.',
        'ru': 'Текст слишком длинный. Максимальная длина — {max_chars} символов.',
        'uk': 'Текст надто довгий. Максимальна довжина — {max_chars} символів.',
    },
    'truth_reply_required': {
        'en': 'Reply to a message to use /truth.',
        'ru': 'Ответьте на сообщение, чтобы использовать /truth.',
        'uk': 'Дайте відповідь на повідомлення, щоб використати /truth.',
    },
    'replied_no_text': {
        'en': 'The replied message does not contain text to analyze.',
        'ru': 'В сообщении, на которое вы ответили, нет текста для анализа.',
        'uk': 'У повідомленні, на яке ви відповіли, немає тексту для аналізу.',
    },
    'sum_need_text': {
        'en': 'Reply to a message or provide text after /sum.',
        'ru': 'Ответьте на сообщение или добавьте текст после /sum.',
        'uk': 'Дайте відповідь на повідомлення або додайте текст після /sum.',
    },
    'fun_need_text': {
        'en': 'Provide text after /fun or reply to a message.',
        'ru': 'Добавьте текст после /fun или ответьте на сообщение.',
        'uk': 'Додайте текст після /fun або дайте відповідь на повідомлення.',
    },
    'provider_timeout': {
        'en': 'The AI provider timed out. Please try again in a moment.',
        'ru': 'AI-провайдер не ответил вовремя. Попробуйте ещё раз чуть позже.',
        'uk': 'AI-провайдер не відповів вчасно. Спробуйте ще раз трохи пізніше.',
    },
    'provider_rate_limit': {
        'en': 'The AI provider rate-limited the request. Please try again shortly.',
        'ru': 'AI-провайдер временно ограничил запросы. Попробуйте ещё раз немного позже.',
        'uk': 'AI-провайдер тимчасово обмежив запити. Спробуйте ще раз трохи пізніше.',
    },
    'provider_unavailable': {
        'en': 'The AI provider is temporarily unavailable. Please try again later.',
        'ru': 'AI-провайдер временно недоступен. Попробуйте позже.',
        'uk': 'AI-провайдер тимчасово недоступний. Спробуйте пізніше.',
    },
    'provider_invalid': {
        'en': 'The AI provider returned an invalid response. Please try again.',
        'ru': 'AI-провайдер вернул некорректный ответ. Попробуйте ещё раз.',
        'uk': 'AI-провайдер повернув некоректну відповідь. Спробуйте ще раз.',
    },
    'admin_only': {
        'en': 'Only chat admins can use this command.',
        'ru': 'Только администраторы чата могут использовать эту команду.',
        'uk': 'Лише адміністратори чату можуть використовувати цю команду.',
    },
}


def text(key: str, language: str, **kwargs) -> str:
    normalized = normalize_language_code(language, fallback='ru')
    variants = _MESSAGES[key]
    template = variants.get(normalized) or variants['ru']
    return template.format(**kwargs)
