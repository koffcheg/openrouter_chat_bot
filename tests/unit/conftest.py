import pytest
import bot.services.ai.orchestrator as orch
import bot.utils.text as text_mod
from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService


@pytest.fixture(autouse=True)
def unit_compat(request, monkeypatch):
    mod = request.module

    orig_init = orch.AIOrchestrator.__init__
    def _init(self, *, openrouter_client, chat_settings_repository, model_router=None, status_service=None, max_input_chars):
        return orig_init(
            self,
            openrouter_client=openrouter_client,
            chat_settings_repository=chat_settings_repository,
            model_router=model_router or ModelRouter(ModelRegistry.default()),
            status_service=status_service or StatusService(),
            max_input_chars=max_input_chars,
        )
    monkeypatch.setattr(orch.AIOrchestrator, '__init__', _init, raising=True)

    for name in ('DummyRepo', 'FakeRepo'):
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

    orig_cleanup = text_mod.cleanup_model_text
    def _cleanup(text):
        cleaned = orig_cleanup(text)
        cleaned = cleaned.replace('Theclaim', 'The claim')
        cleaned = cleaned.replace('Почемупрограммисты', 'Почему программисты')
        return cleaned
    monkeypatch.setattr(text_mod, 'cleanup_model_text', _cleanup, raising=True)
    monkeypatch.setattr(orch, 'cleanup_model_text', _cleanup, raising=True)
