from bot.config.settings import Settings


def test_settings_parse_owner_ids() -> None:
    settings = Settings(BOT_TOKEN="token", OPENROUTER_API_KEY="key", OWNER_USER_IDS="1, 2,3")
    assert settings.owner_ids == [1, 2, 3]
    assert settings.openrouter_default_model == "nvidia/nemotron-3-super-120b-a12b:free"
