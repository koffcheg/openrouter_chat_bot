from __future__ import annotations

from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault

DEFAULT_COMMANDS = [
    BotCommand(command='start', description='start the bot'),
    BotCommand(command='help', description='show help'),
    BotCommand(command='about', description='about CumxAI'),
    BotCommand(command='ask', description='ask a question'),
    BotCommand(command='truth', description='analyze a replied claim'),
    BotCommand(command='sum', description='summarize a replied message'),
    BotCommand(command='fun', description='playful answer'),
    BotCommand(command='status', description='bot status'),
    BotCommand(command='models', description='available models'),
    BotCommand(command='setmodel', description='set current model'),
    BotCommand(command='pause', description='pause replies'),
    BotCommand(command='resume', description='resume replies'),
    BotCommand(command='setlang', description='set reply language'),
    BotCommand(command='setstyle', description='set response style'),
    BotCommand(command='viewsettings', description='show current settings'),
    BotCommand(command='resetsettings', description='reset chat settings'),
]

RU_COMMANDS = [
    BotCommand(command='start', description='запустить бота'),
    BotCommand(command='help', description='показать помощь'),
    BotCommand(command='about', description='о CumxAI'),
    BotCommand(command='ask', description='задать вопрос'),
    BotCommand(command='truth', description='проверить утверждение в ответе'),
    BotCommand(command='sum', description='кратко пересказать сообщение'),
    BotCommand(command='fun', description='лёгкий шуточный ответ'),
    BotCommand(command='status', description='статус бота'),
    BotCommand(command='models', description='доступные модели'),
    BotCommand(command='setmodel', description='выбрать текущую модель'),
    BotCommand(command='pause', description='поставить ответы на паузу'),
    BotCommand(command='resume', description='возобновить ответы'),
    BotCommand(command='setlang', description='язык ответов'),
    BotCommand(command='setstyle', description='стиль ответов'),
    BotCommand(command='viewsettings', description='показать текущие настройки'),
    BotCommand(command='resetsettings', description='сбросить настройки чата'),
]

UA_COMMANDS = [
    BotCommand(command='start', description='запустити бота'),
    BotCommand(command='help', description='показати довідку'),
    BotCommand(command='about', description='про CumxAI'),
    BotCommand(command='ask', description='поставити запитання'),
    BotCommand(command='truth', description='перевірити твердження у відповіді'),
    BotCommand(command='sum', description='коротко переказати повідомлення'),
    BotCommand(command='fun', description='легка жартівлива відповідь'),
    BotCommand(command='status', description='статус бота'),
    BotCommand(command='models', description='доступні моделі'),
    BotCommand(command='setmodel', description='вибрати поточну модель'),
    BotCommand(command='pause', description='поставити відповіді на паузу'),
    BotCommand(command='resume', description='відновити відповіді'),
    BotCommand(command='setlang', description='мова відповідей'),
    BotCommand(command='setstyle', description='стиль відповідей'),
    BotCommand(command='viewsettings', description='показати поточні налаштування'),
    BotCommand(command='resetsettings', description='скинути налаштування чату'),
]


async def register_bot_commands(bot: Bot) -> None:
    scope = BotCommandScopeDefault()
    await bot.set_my_commands(DEFAULT_COMMANDS, scope=scope)
    await bot.set_my_commands(RU_COMMANDS, scope=scope, language_code='ru')
    await bot.set_my_commands(UA_COMMANDS, scope=scope, language_code='uk')
