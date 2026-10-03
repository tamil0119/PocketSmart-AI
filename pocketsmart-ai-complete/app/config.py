from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    app_env: str = "development"
    secret_key: str = "dev-only-change-me"
    database_url: str = f"sqlite:///{BASE_DIR / 'pocketsmart.db'}"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"
    use_gemini: bool = True
    max_upload_mb: int = 5
    allowed_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]

@lru_cache
def get_settings() -> Settings:
    return Settings()
