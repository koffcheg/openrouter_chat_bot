def test_import_smoke() -> None:
    import bot
    import bot.main
    import bot.config.settings

    assert bot is not None
