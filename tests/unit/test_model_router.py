from bot.services.ai.model_registry import ModelRegistry
from bot.services.ai.router import ModelRouter


def test_model_sequence_skips_llama_for_ukrainian_path():
    router = ModelRouter(ModelRegistry.default())
    sequence = router.model_sequence('nvidia/nemotron-3-super-120b-a12b:free', 'uk')
    assert sequence == ['nvidia/nemotron-3-super-120b-a12b:free', 'openrouter/free']


def test_model_sequence_keeps_llama_for_english_path():
    router = ModelRouter(ModelRegistry.default())
    sequence = router.model_sequence('nvidia/nemotron-3-super-120b-a12b:free', 'en')
    assert sequence == ['nvidia/nemotron-3-super-120b-a12b:free', 'meta-llama/llama-3.3-70b-instruct:free', 'openrouter/free']
