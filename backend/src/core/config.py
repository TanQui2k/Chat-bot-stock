from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

DEFAULT_SECRET_KEY = "your-secret-key-here-change-in-production"


class Settings(BaseSettings):
    # Server
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000
    ENVIRONMENT: str = "development"
    TRUST_PROXY_HEADERS: bool = False

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:your_password@localhost:5432/stock_db"

    # OpenAI
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str | None = None

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

# SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)


@event.listens_for(engine, "connect")
def _set_client_encoding(dbapi_connection, connection_record):  # type: ignore[no-redef]
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET client_encoding TO 'UTF8'")
        cursor.close()
    except Exception:
        # Best effort: do not block app startup if the DB/driver does not support it.
        pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
