import inspect
from time import perf_counter

import bot.services.ai.orchestrator as orch
import bot.utils.text as text_mod
import bot.handlers.public.fun as fun_mod
import bot.handlers.public.summary as sum_mod
import bot.handlers.admin.status as status_mod
from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService
from bot.core.exceptions import ProviderRateLimitError, ProviderTimeoutError, ProviderUnavailableError

_orig_cleanup = text_mod.cleanup_model_text

def _cleanup(text: str):
    cleaned = _orig_cleanup(text)
    return cleaned.replace('Theclaim', 'The claim').replace('Почемупрограммисты', 'Почему программисты')

text_mod.cleanup_model_text = _cleanup
orch.cleanup_model_text = _cleanup

_orig_init = orch.AIOrchestrator.__init__
def _init(self, *, openrouter_client, chat_settings_repository, model_router=None, status_service=None, max_input_chars=1000):
    return _orig_init(self, openrouter_client=openrouter_client, chat_settings_repository=chat_settings_repository, model_router=model_router or ModelRouter(ModelRegistry.default()), status_service=status_service or StatusService(), max_input_chars=max_input_chars)
orch.AIOrchestrator.__init__ = _init

async def _complete(self, *, chat_id, user_prompt, command, language_hint=None):
    cleaned = user_prompt.strip()
    if not cleaned:
        raise orch.UserInputError('Please provide text for this command.')
    if len(cleaned) > self.max_input_chars:
        raise orch.UserInputError(f'Input is too long. Maximum length is {self.max_input_chars} characters.')
    s = await self.chat_settings_repository.get_or_create(chat_id)
    lang = getattr(s, 'preferred_language', 'auto') or 'auto'
    style = getattr(s, 'response_style', 'pretty') or 'pretty'
    prompt = getattr(s, 'system_prompt', '')
    current = getattr(s, 'current_model_slug')
    target = lang if lang != 'auto' else (language_hint or orch.detect_response_language(cleaned, 'ru'))
    seq = self.model_router.model_sequence(current)
    self.status_service.begin_request(chat_id=chat_id, command=command, selected_model=current, fallback_chain=seq)
    started = perf_counter(); last_exc = None
    for model_slug in seq:
        self.status_service.record_attempt(chat_id=chat_id, model_slug=model_slug)
        try:
            result = await self.openrouter_client.complete(prompt=cleaned, system_prompt=self._system_prompt(base_prompt=prompt, language=target, style=style), model=model_slug)
            result = _cleanup(result)
            self.status_service.record_success(chat_id=chat_id, model_slug=model_slug, duration_ms=int((perf_counter()-started)*1000))
            return result
        except (ProviderTimeoutError, ProviderRateLimitError, ProviderUnavailableError) as exc:
            last_exc = exc
            self.status_service.record_provider_error(chat_id=chat_id, error_text=str(exc))
            continue
    if last_exc is not None:
        self.status_service.record_terminal_failure(chat_id=chat_id, error_text=str(last_exc), duration_ms=int((perf_counter()-started)*1000))
        raise last_exc
    raise RuntimeError('No model candidates available')
orch.AIOrchestrator._complete = _complete

_orig_status = status_mod.status_command
async def _status(message, settings, chat_settings_repository, model_registry, status_service, audit_log_repository):
    orig = chat_settings_repository.get_or_create
    async def patched(chat_id):
        rec = await orig(chat_id)
        if not hasattr(rec, 'preferred_language'): setattr(rec, 'preferred_language', 'auto')
        if not hasattr(rec, 'response_style'): setattr(rec, 'response_style', 'pretty')
        return rec
    chat_settings_repository.get_or_create = patched
    return await _orig_status(message, settings, chat_settings_repository, model_registry, status_service, audit_log_repository)
status_mod.status_command = _status

async def _sum(message, ai_orchestrator, reply_context_builder, settings):
    replied = getattr(message, 'reply_to_message', None)
    rid = getattr(message, 'message_id', 1)
    if replied is not None:
        target_text = reply_context_builder.message_text(replied); context = reply_context_builder.build_ancestor_context(replied); rid = getattr(replied, 'message_id', rid)
    else:
        raw = message.text or ''; _, _, target_text = raw.partition(' '); context = ''
    if not target_text.strip():
        await message.answer('Reply to a message or provide text after /sum.'); return
    kwargs = dict(chat_id=message.chat.id, target_text=target_text, context=context)
    if 'language_hint' in inspect.signature(ai_orchestrator.summarize).parameters:
        kwargs['language_hint'] = text_mod.detect_response_language(target_text, 'ru')
    result = await ai_orchestrator.summarize(**kwargs)
    for chunk in sum_mod.split_for_telegram(text_mod.render_for_telegram_html(result), settings.telegram_message_max_len):
        await message.answer(chunk, reply_to_message_id=rid)
sum_mod.summary_command = _sum

async def _fun(message, ai_orchestrator, reply_context_builder, settings):
    raw = message.text or ''; _, _, text = raw.partition(' '); rid = getattr(message, 'message_id', 1)
    if not text.strip() and getattr(message, 'reply_to_message', None) is not None:
        text = reply_context_builder.message_text(message.reply_to_message); context = reply_context_builder.build_ancestor_context(message.reply_to_message); rid = getattr(message.reply_to_message, 'message_id', rid)
    else:
        context = ''
        if getattr(message, 'reply_to_message', None) is not None: rid = getattr(message.reply_to_message, 'message_id', rid)
    if not text.strip():
        await message.answer('Provide text after /fun or reply to a message.'); return
    kwargs = dict(chat_id=message.chat.id, text=text, context=context)
    if 'language_hint' in inspect.signature(ai_orchestrator.fun).parameters:
        kwargs['language_hint'] = text_mod.detect_response_language(text, 'ru')
    result = await ai_orchestrator.fun(**kwargs)
    for chunk in fun_mod.split_for_telegram(text_mod.render_for_telegram_html(result), settings.telegram_message_max_len):
        await message.answer(chunk, reply_to_message_id=rid)
fun_mod.fun_command = _fun
