from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.config.settings import Settings
from bot.repositories.audit_log import AuditLogRepository
from bot.repositories.chat_settings import ChatSettingsRepository
from bot.services.telegram.admin_checks import ensure_admin

router = Router(name="admin_control")


def _ui_lang(preferred_language: str) -> str:
    if preferred_language in {'ua', 'uk'}:
        return 'ua'
    if preferred_language == 'en':
        return 'en'
    return 'ru'


def _texts(lang: str) -> dict[str, str]:
    if lang == 'en':
        return {
            'paused': 'Bot responses are paused for this chat.',
            'resumed': 'Bot responses are enabled for this chat.',
            'setlang_usage': 'Usage: /setlang auto|ru|ua|en',
            'setstyle_usage': 'Usage: /setstyle pretty|concise|playful',
            'lang_set': 'Preferred language set to {value}',
            'style_set': 'Response style set to {value}',
            'viewsettings': 'Current settings:\nlanguage: {language}\nstyle: {style}\nmodel: {model}\npaused: {paused}',
            'resetsettings': 'Chat settings were reset to defaults.',
        }
    if lang == 'ua':
        return {
            'paused': 'Відповіді бота поставлено на паузу для цього чату.',
            'resumed': 'Відповіді бота знову увімкнені для цього чату.',
            'setlang_usage': 'Використання: /setlang auto|ru|ua|en',
            'setstyle_usage': 'Використання: /setstyle pretty|concise|playful',
            'lang_set': 'Мову відповідей встановлено: {value}',
            'style_set': 'Стиль відповідей встановлено: {value}',
            'viewsettings': 'Поточні налаштування:\nмова: {language}\nстиль: {style}\nмодель: {model}\nпауза: {paused}',
            'resetsettings': 'Налаштування чату скинуто до типових значень.',
        }
    return {
        'paused': 'Ответы бота поставлены на паузу для этого чата.',
        'resumed': 'Ответы бота снова включены для этого чата.',
        'setlang_usage': 'Использование: /setlang auto|ru|ua|en',
        'setstyle_usage': 'Использование: /setstyle pretty|concise|playful',
        'lang_set': 'Язык ответов установлен: {value}',
        'style_set': 'Стиль ответов установлен: {value}',
        'viewsettings': 'Текущие настройки:\nязык: {language}\nстиль: {style}\nмодель: {model}\nпауза: {paused}',
        'resetsettings': 'Настройки чата сброшены к значениям по умолчанию.',
    }


@router.message(Command("pause"))
async def pause_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(previous.preferred_language)
    texts = _texts(lang)
    updated = await chat_settings_repository.set_paused(message.chat.id, True)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='pause', old_value={'is_paused': previous.is_paused}, new_value={'is_paused': updated.is_paused})
    await message.answer(texts['paused'])


@router.message(Command("resume"))
async def resume_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(previous.preferred_language)
    texts = _texts(lang)
    updated = await chat_settings_repository.set_paused(message.chat.id, False)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='resume', old_value={'is_paused': previous.is_paused}, new_value={'is_paused': updated.is_paused})
    await message.answer(texts['resumed'])


@router.message(Command("setlang"))
async def setlang_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(previous.preferred_language)
    texts = _texts(lang)
    raw_text = message.text or ''
    _, _, value = raw_text.partition(' ')
    value = value.strip().lower()
    if value == 'ua':
        value = 'uk'
    if value not in {'auto', 'ru', 'uk', 'en'}:
        await message.answer(texts['setlang_usage'])
        return
    updated = await chat_settings_repository.set_language(message.chat.id, value)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='setlang', old_value={'preferred_language': previous.preferred_language}, new_value={'preferred_language': updated.preferred_language})
    shown = 'ua' if updated.preferred_language == 'uk' else updated.preferred_language
    await message.answer(texts['lang_set'].format(value=shown))


@router.message(Command("setstyle"))
async def setstyle_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(previous.preferred_language)
    texts = _texts(lang)
    raw_text = message.text or ''
    _, _, value = raw_text.partition(' ')
    value = value.strip().lower()
    if value not in {'pretty', 'concise', 'playful'}:
        await message.answer(texts['setstyle_usage'])
        return
    updated = await chat_settings_repository.set_style(message.chat.id, value)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='setstyle', old_value={'response_style': previous.response_style}, new_value={'response_style': updated.response_style})
    await message.answer(texts['style_set'].format(value=updated.response_style))


@router.message(Command("viewsettings"))
async def viewsettings_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    record = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(record.preferred_language)
    texts = _texts(lang)
    shown = 'ua' if record.preferred_language == 'uk' else record.preferred_language
    paused = 'yes' if record.is_paused else 'no'
    if lang == 'ua':
        paused = 'так' if record.is_paused else 'ні'
    elif lang == 'ru':
        paused = 'да' if record.is_paused else 'нет'
    await message.answer(texts['viewsettings'].format(language=shown, style=record.response_style, model=record.current_model_slug, paused=paused))


@router.message(Command("resetsettings"))
async def resetsettings_command(message: Message, settings: Settings, chat_settings_repository: ChatSettingsRepository, audit_log_repository: AuditLogRepository) -> None:
    if not await ensure_admin(message, settings):
        return
    previous = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_lang(previous.preferred_language)
    texts = _texts(lang)
    updated = await chat_settings_repository.reset_preferences(message.chat.id)
    await audit_log_repository.append(chat_id=message.chat.id, actor_user_id=message.from_user.id if message.from_user else 0, action='resetsettings', old_value={'preferred_language': previous.preferred_language, 'response_style': previous.response_style}, new_value={'preferred_language': updated.preferred_language, 'response_style': updated.response_style})
    await message.answer(texts['resetsettings'])
