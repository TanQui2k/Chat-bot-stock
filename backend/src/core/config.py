from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

DEFAULT_SECRET_KEY = "your-secret-key-here-change-in-production"


class Settings(BaseSettings):
    # Server
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000
    ENVIRONMENT: str = "development"
    TRUST_PROXY_HEADERS: bool = False
    AUTO_START_LOCAL_DB: bool = True

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:your_password@localhost:5432/stock_db"

    # OpenAI
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str | None = None

    # Market data
    VNSTOCK_API_KEY: str | None = None

    # Security
    SECRET_KEY: str = DEFAULT_SECRET_KEY

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

if settings.ENVIRONMENT.lower() == "production" and settings.SECRET_KEY == DEFAULT_SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be changed before running in production.")
