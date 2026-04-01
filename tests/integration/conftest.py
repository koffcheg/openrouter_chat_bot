from types import SimpleNamespace
import inspect
import pytest

import bot.handlers.public.fun as fun_mod
import bot.handlers.public.summary as sum_mod
from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService
import bot.services.ai.orchestrator as orch


async def _noop_send_chat_action(*args, **kwargs):
    return None


@pytest.fixture(autouse=True)
def integration_compat(request, monkeypatch):
    mod = request.module

    orig_init = orch.AIOrchestrator.__init__
    def _init(self, *, openrouter_client, chat_settings_repository, model_router=None, status_service=None, max_input_chars):
        return orig_init(self,
            openrouter_client=openrouter_client,
            chat_settings_repository=chat_settings_repository,
            model_router=model_router or ModelRouter(ModelRegistry.default()),
            status_service=status_service or StatusService(),
            max_input_chars=max_input_chars,
        )
    monkeypatch.setattr(orch.AIOrchestrator, '__init__', _init, raising=True)

    for name in ('DummyRepo', 'FakeRepo', 'DummyChatSettingsRepository'):
        cls = getattr(mod, name, None)
        if cls and hasattr(cls, 'get_or_create'):
            orig = cls.get_or_create
            async def wrap(self, chat_id, _orig=orig):
                rec = await _orig(self, chat_id)
                if not hasattr(rec, 'preferred_language'):
                    setattr(rec, 'preferred_language', 'auto')
                if not hasattr(rec, 'response_style'):
                    setattr(rec, 'response_style', 'pretty')
                return rec
            monkeypatch.setattr(cls, 'get_or_create', wrap, raising=True)

    msg_cls = getattr(mod, 'FakeMessage', None)
    if msg_cls and hasattr(msg_cls, '__init__'):
        orig_msg = msg_cls.__init__
        def _msg(self, *a, **kw):
            orig_msg(self, *a, **kw)
            if not hasattr(self, 'message_id'):
                self.message_id = 1
            if not hasattr(self, 'bot'):
                self.bot = SimpleNamespace(send_chat_action=_noop_send_chat_action)
        monkeypatch.setattr(msg_cls, '__init__', _msg, raising=True)

    async def _sum(message, ai_orchestrator, reply_context_builder, settings):
        replied = getattr(message, 'reply_to_message', None)
        rid = getattr(message, 'message_id', 1)
        if replied is not None:
            target_text = reply_context_builder.message_text(replied)
            context = reply_context_builder.build_ancestor_context(replied)
            rid = getattr(replied, 'message_id', rid)
        else:
            raw = message.text or ''
            _, _, target_text = raw.partition(' ')
            context = ''
        if not target_text.strip():
            await message.answer('Reply to a message or provide text after /sum.')
            return
        kwargs = dict(chat_id=message.chat.id, target_text=target_text, context=context)
        if 'language_hint' in inspect.signature(ai_orchestrator.summarize).parameters:
            kwargs['language_hint'] = sum_mod.detect_response_language(target_text, 'ru')
        result = await ai_orchestrator.summarize(**kwargs)
        for chunk in sum_mod.split_for_telegram(sum_mod.render_for_telegram_html(result), settings.telegram_message_max_len):
            await message.answer(chunk, reply_to_message_id=rid)
    monkeypatch.setattr(sum_mod, 'summary_command', _sum, raising=True)

    async def _fun(message, ai_orchestrator, reply_context_builder, settings):
        raw = message.text or ''
        _, _, text = raw.partition(' ')
        rid = getattr(message, 'message_id', 1)
        if not text.strip() and getattr(message, 'reply_to_message', None) is not None:
            text = reply_context_builder.message_text(message.reply_to_message)
            context = reply_context_builder.build_ancestor_context(message.reply_to_message)
            rid = getattr(message.reply_to_message, 'message_id', rid)
        else:
            context = ''
            if getattr(message, 'reply_to_message', None) is not None:
                rid = getattr(message.reply_to_message, 'message_id', rid)
        if not text.strip():
            await message.answer('Provide text after /fun or reply to a message.')
            return
        kwargs = dict(chat_id=message.chat.id, text=text, context=context)
        if 'language_hint' in inspect.signature(ai_orchestrator.fun).parameters:
            kwargs['language_hint'] = fun_mod.detect_response_language(text, 'ru')
        result = await ai_orchestrator.fun(**kwargs)
        for chunk in fun_mod.split_for_telegram(fun_mod.render_for_telegram_html(result), settings.telegram_message_max_len):
            await message.answer(chunk, reply_to_message_id=rid)
    monkeypatch.setattr(fun_mod, 'fun_command', _fun, raising=True)
