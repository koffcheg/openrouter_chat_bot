from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.repositories.chat_settings import ChatSettingsRepository

router = Router(name="public_help")

TEXTS = {
    'ru': {
        'start': """Привет. Я CumxAI, ассистент этого чата.

Используй /help, чтобы посмотреть доступные команды.
Администраторы также могут использовать /status, /models, /setmodel, /pause, /resume, /setlang, /setstyle, /viewsettings и /resetsettings.""",
        'help': """Доступные команды:
/start — показать короткое приветствие
/help — показать эту справку
/about — узнать, что умеет CumxAI
/ask [text] — задать вопрос
/truth — ответом на сообщение проверить утверждение
/sum — кратко пересказать сообщение
/fun [text] — лёгкий шуточный ответ

Команды администратора:
/status — показать текущий статус бота
/models — показать доступные модели
/setmodel &lt;slug&gt; — выбрать текущую модель
/pause — поставить ответы бота на паузу
/resume — возобновить ответы бота
/setlang auto|ru|ua|en — язык ответов
/setstyle pretty|concise|playful — стиль ответов
/viewsettings — показать текущие настройки
/resetsettings — сбросить настройки чата""",
        'about': """<b>CumxAI</b> — ассистент этого чата.

Что умеет:
• /ask [text] — ответить на вопрос
• /truth — проанализировать утверждение в ответе на сообщение
• /sum — кратко пересказать сообщение
• /fun [text] — лёгкий шуточный ответ
• /about — кратко о боте

Важно:
• это не режим живой проверки интернета
• язык ответа обычно совпадает с языком пользователя
• если язык неясен, по умолчанию используется русский
• администраторы могут менять язык, стиль и модель ответов""",
    },
    'ua': {
        'start': """Привіт. Я CumxAI, асистент цього чату.

Використовуй /help, щоб побачити доступні команди.
Адміністратори також можуть використовувати /status, /models, /setmodel, /pause, /resume, /setlang, /setstyle, /viewsettings і /resetsettings.""",
        'help': """Доступні команди:
/start — показати коротке привітання
/help — показати цю довідку
/about — дізнатися, що вміє CumxAI
/ask [text] — поставити запитання
/truth — у відповіді на повідомлення перевірити твердження
/sum — коротко переказати повідомлення
/fun [text] — легка жартівлива відповідь

Команди адміністратора:
/status — показати поточний статус бота
/models — показати доступні моделі
/setmodel &lt;slug&gt; — вибрати поточну модель
/pause — поставити відповіді бота на паузу
/resume — відновити відповіді бота
/setlang auto|ru|ua|en — мова відповідей
/setstyle pretty|concise|playful — стиль відповідей
/viewsettings — показати поточні налаштування
/resetsettings — скинути налаштування чату""",
        'about': """<b>CumxAI</b> — асистент цього чату.

Що вміє:
• /ask [text] — відповісти на запитання
• /truth — проаналізувати твердження у відповіді на повідомлення
• /sum — коротко переказати повідомлення
• /fun [text] — легка жартівлива відповідь
• /about — коротко про бота

Важливо:
• це не режим живої перевірки інтернету
• мова відповіді зазвичай збігається з мовою користувача
• якщо мова неясна, за замовчуванням використовується російська
• адміністратори можуть змінювати мову, стиль і модель відповідей""",
    },
    'en': {
        'start': """Hi. I am CumxAI, the assistant for this chat.

Use /help to see the available commands.
Admins can also use /status, /models, /setmodel, /pause, /resume, /setlang, /setstyle, /viewsettings, and /resetsettings.""",
        'help': """Available commands:
/start — show a short welcome message
/help — show this help
/about — learn what CumxAI can do
/ask [text] — ask the assistant a question
/truth — reply to a message to analyze the claim
/sum — reply to a message to summarize it
/fun [text] — playful answer mode

Admin commands:
/status — show current bot status
/models — list available models
/setmodel &lt;slug&gt; — set the current model
/pause — pause bot replies in this chat
/resume — resume bot replies in this chat
/setlang auto|ru|ua|en — set reply language
/setstyle pretty|concise|playful — set response style
/viewsettings — show current settings
/resetsettings — reset chat settings""",
        'about': """<b>CumxAI</b> is the assistant for this chat.

What it can do:
• /ask [text] — answer a question
• /truth — analyze a claim in a replied message
• /sum — summarize a message
• /fun [text] — playful answer mode
• /about — about the bot

Important:
• this is not a live internet verification mode
• the reply language usually follows the user's language
• if the language is unclear, Russian is used by default
• admins can change the reply language, style, and model""",
    },
}


def _ui_language(preferred_language: str) -> str:
    if preferred_language in {'ua', 'uk'}:
        return 'ua'
    if preferred_language == 'en':
        return 'en'
    return 'ru'


@router.message(Command("start"))
async def start_command(message: Message, chat_settings_repository: ChatSettingsRepository) -> None:
    settings = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_language(settings.preferred_language)
    await message.answer(TEXTS[lang]['start'])


@router.message(Command("help"))
async def help_command(message: Message, chat_settings_repository: ChatSettingsRepository) -> None:
    settings = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_language(settings.preferred_language)
    await message.answer(TEXTS[lang]['help'])


@router.message(Command("about"))
async def about_command(message: Message, chat_settings_repository: ChatSettingsRepository) -> None:
    settings = await chat_settings_repository.get_or_create(message.chat.id)
    lang = _ui_language(settings.preferred_language)
    await message.answer(TEXTS[lang]['about'])
