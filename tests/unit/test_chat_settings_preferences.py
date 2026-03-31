import pytest

from bot.db.sqlite import connect, initialize_database
from bot.repositories.chat_settings import ChatSettingsRepository


@pytest.mark.asyncio
async def test_chat_settings_preferences_roundtrip(tmp_path):
    db = await connect(str(tmp_path / 'bot.db'), 5000)
    await initialize_database(db)
    repo = ChatSettingsRepository(db)
    record = await repo.get_or_create(100)
    assert record.preferred_language == 'auto'
    assert record.response_style == 'pretty'
    updated_lang = await repo.set_language(100, 'ru')
    updated_style = await repo.set_style(100, 'concise')
    assert updated_lang.preferred_language == 'ru'
    assert updated_style.response_style == 'concise'
    fetched = await repo.get_or_create(100)
    assert fetched.preferred_language == 'ru'
    assert fetched.response_style == 'concise'
    await db.close()
