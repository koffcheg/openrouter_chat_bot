from bot.services.ai.model_registry import ModelRegistry


def test_model_registry_has_enabled_default_and_free_fallbacks():
    registry = ModelRegistry.default()
    enabled = registry.list_enabled()
    assert any(entry.is_default for entry in enabled)
    assert registry.is_enabled('openrouter/free') is True
    assert registry.is_enabled('nvidia/nemotron-3-super-120b-a12b:free') is True
