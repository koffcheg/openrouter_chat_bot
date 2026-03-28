from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = ""
    openrouter_api_key: str = ""
    openrouter_default_model: str = "nvidia/nemotron-3-super-120b-a12b:free"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
