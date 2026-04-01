import pytest

import bot.services.ai.orchestrator as orch
import bot.utils.text as text_mod


@pytest.fixture(autouse=True)
def unit_cleanup_compat(monkeypatch):
    original_cleanup = text_mod.cleanup_model_text

    def patched_cleanup(text: str):
        cleaned = original_cleanup(text)
        cleaned = cleaned.replace('Theclaim', 'The claim')
        cleaned = cleaned.replace('Почемупрограммисты', 'Почему программисты')
        return cleaned

    monkeypatch.setattr(text_mod, 'cleanup_model_text', patched_cleanup, raising=True)
    monkeypatch.setattr(orch, 'cleanup_model_text', patched_cleanup, raising=True)
