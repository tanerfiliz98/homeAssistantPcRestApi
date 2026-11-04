from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
    )

    api_key: str = "change-me-to-a-long-random-secret"
    host: str = "0.0.0.0"
    port: int = 8765
    mdns_enabled: bool = True
    mdns_name: str = "ha-pc"


settings = Settings()
