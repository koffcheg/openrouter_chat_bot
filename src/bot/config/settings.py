from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from bot.core.constants import DEFAULT_CHAT_MODEL


class Settings(BaseSettings):
    bot_token: str = Field(..., alias="BOT_TOKEN")
    bot_username: str = Field(default="", alias="BOT_USERNAME")
    owner_user_ids: str = Field(default="", alias="OWNER_USER_IDS")

    openrouter_api_key: str = Field(..., alias="OPENROUTER_API_KEY")
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    openrouter_default_model: str = Field(default=DEFAULT_CHAT_MODEL, alias="OPENROUTER_DEFAULT_MODEL")
    openrouter_http_referer: str = Field(default="", alias="OPENROUTER_HTTP_REFERER")
    openrouter_app_title: str = Field(default="openrouter_chat_bot", alias="OPENROUTER_APP_TITLE")

    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")
    tz: str = Field(default="UTC", alias="TZ")

    sqlite_path: str = Field(default="/app/data/bot.db", alias="SQLITE_PATH")
    sqlite_busy_timeout_ms: int = Field(default=5000, alias="SQLITE_BUSY_TIMEOUT_MS")

    default_user_cooldown_seconds: int = Field(default=20, alias="DEFAULT_USER_COOLDOWN_SECONDS")
    default_user_daily_quota: int = Field(default=25, alias="DEFAULT_USER_DAILY_QUOTA")
    default_chat_burst_limit: int = Field(default=8, alias="DEFAULT_CHAT_BURST_LIMIT")
    default_chat_burst_window_seconds: int = Field(default=60, alias="DEFAULT_CHAT_BURST_WINDOW_SECONDS")
    max_input_chars: int = Field(default=4000, alias="MAX_INPUT_CHARS")
    max_context_messages: int = Field(default=8, alias="MAX_CONTEXT_MESSAGES")
    max_context_chars: int = Field(default=12000, alias="MAX_CONTEXT_CHARS")
    request_timeout_seconds: float = Field(default=60.0, alias="REQUEST_TIMEOUT_SECONDS")

    telegram_message_max_len: int = Field(default=4096, alias="TELEGRAM_MESSAGE_MAX_LEN")
    telegram_parse_mode: str = Field(default="HTML", alias="TELEGRAM_PARSE_MODE")

    polling_allowed_updates: str = Field(default="message,edited_message", alias="POLLING_ALLOWED_UPDATES")
    polling_drop_pending_updates: bool = Field(default=False, alias="POLLING_DROP_PENDING_UPDATES")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def owner_ids(self) -> list[int]:
        if not self.owner_user_ids.strip():
            return []
        return [int(part.strip()) for part in self.owner_user_ids.split(",") if part.strip()]

    @property
    def polling_allowed_updates_list(self) -> list[str]:
        return [part.strip() for part in self.polling_allowed_updates.split(",") if part.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
