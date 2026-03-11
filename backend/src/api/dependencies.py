from src.core.config import SessionLocal

def get_db():
    """Generator cung cấp session DB cho từng request API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
