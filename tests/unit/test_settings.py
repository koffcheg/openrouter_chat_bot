from bot.config.settings import Settings


def test_settings_has_expected_default_model() -> None:
    settings = Settings()
    assert settings.openrouter_default_model == "nvidia/nemotron-3-super-120b-a12b:free"
