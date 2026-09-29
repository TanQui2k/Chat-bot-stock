"""Database engine and session lifecycle.

Application settings live in ``config.py``; SQLAlchemy wiring lives here so
scripts, API dependencies, and tests have one clear database entry point.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from src.core.config import settings


engine = create_engine(settings.DATABASE_URL)


@event.listens_for(engine, "connect")
def _set_client_encoding(dbapi_connection, connection_record):  # type: ignore[no-redef]
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SET client_encoding TO 'UTF8'")
        cursor.close()
    except Exception:
        # Best effort: do not block startup for unsupported drivers/databases.
        pass


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
