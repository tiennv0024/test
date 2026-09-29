from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://eureka:eureka@localhost:5432/eureka_music"
    audio_storage_path: Path = Path("storage/tracks")
    allowed_audio_extensions: set[str] = {".mp3", ".wav", ".flac", ".ogg", ".m4a"}

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.audio_storage_path.mkdir(parents=True, exist_ok=True)
    return settings
