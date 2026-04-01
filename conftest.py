from types import SimpleNamespace
import pytest
import bot.services.ai.orchestrator as orch
from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.router import ModelRouter
from bot.services.health.status_service import StatusService


async def _noop_send_chat_action(*args, **kwargs):
    return None


@pytest.fixture(autouse=True)
def compat(request, monkeypatch):
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
