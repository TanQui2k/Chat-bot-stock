from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Server Configuration
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:your_password@localhost:5432/stock_db"

    # OpenAI
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str | None = None

    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Khởi tạo SQLAlchemy Engine
engine = create_engine(settings.DATABASE_URL)

# Ensure UTF-8 client encoding for Postgres connections (avoid UnicodeEncodeError on Windows locales)
@event.listens_for(engine, "connect")
def _set_client_encoding(dbapi_connection, connection_record):  # type: ignore[no-redef]
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET client_encoding TO 'UTF8'")
        cursor.close()
    except Exception:
        # Best-effort: don't block app startup if DB/driver doesn't support it.
        pass

# Tạo SessionLocal class cho các phiên làm việc với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
