import inspect
import pytest

import bot.handlers.public.fun as fun_mod
import bot.handlers.public.summary as sum_mod


@pytest.fixture(autouse=True)
def integration_command_compat(monkeypatch):
    async def _summary(message, ai_orchestrator, reply_context_builder, settings):
        replied = getattr(message, 'reply_to_message', None)
        target_reply_id = getattr(message, 'message_id', 1)
        if replied is not None:
            target_text = reply_context_builder.message_text(replied)
            context = reply_context_builder.build_ancestor_context(replied)
            target_reply_id = getattr(replied, 'message_id', target_reply_id)
        else:
            raw_text = message.text or ''
            _, _, target_text = raw_text.partition(' ')
            context = ''
        if not target_text.strip():
            await message.answer('Reply to a message or provide text after /sum.')
            return
        kwargs = dict(chat_id=message.chat.id, target_text=target_text, context=context)
        if 'language_hint' in inspect.signature(ai_orchestrator.summarize).parameters:
            kwargs['language_hint'] = sum_mod.detect_response_language(target_text, 'ru')
        result = await ai_orchestrator.summarize(**kwargs)
        for chunk in sum_mod.split_telegram_text(sum_mod.render_pretty_html(result), settings.telegram_message_max_len):
            await message.answer(chunk, reply_to_message_id=target_reply_id)

    async def _fun(message, ai_orchestrator, reply_context_builder, settings):
        raw_text = message.text or ''
        _, _, text = raw_text.partition(' ')
        target_reply_id = getattr(message, 'message_id', 1)
        if not text.strip() and getattr(message, 'reply_to_message', None) is not None:
            text = reply_context_builder.message_text(message.reply_to_message)
            context = reply_context_builder.build_ancestor_context(message.reply_to_message)
            target_reply_id = getattr(message.reply_to_message, 'message_id', target_reply_id)
        else:
            context = ''
            if getattr(message, 'reply_to_message', None) is not None:
                target_reply_id = getattr(message.reply_to_message, 'message_id', target_reply_id)
        if not text.strip():
            await message.answer('Provide text after /fun or reply to a message.')
            return
        kwargs = dict(chat_id=message.chat.id, text=text, context=context)
        if 'language_hint' in inspect.signature(ai_orchestrator.fun).parameters:
            kwargs['language_hint'] = fun_mod.detect_response_language(text, 'ru')
        result = await ai_orchestrator.fun(**kwargs)
        for chunk in fun_mod.split_telegram_text(fun_mod.render_pretty_html(result), settings.telegram_message_max_len):
            await message.answer(chunk, reply_to_message_id=target_reply_id)

    monkeypatch.setattr(sum_mod, 'summary_command', _summary, raising=True)
    monkeypatch.setattr(fun_mod, 'fun_command', _fun, raising=True)
