"""Script to make hashed_password nullable in users table."""

from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from src.core.config import engine

def make_password_nullable():
    """Alter users table to make hashed_password nullable."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("Altering users table: making hashed_password nullable...")
        db.execute(text("""
            ALTER TABLE users 
            ALTER COLUMN hashed_password DROP NOT NULL
        """))
        db.commit()
        print("✓ hashed_password is now nullable!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        # If it already is nullable, this might fail on some DBs, or just do nothing
    finally:
        db.close()

if __name__ == "__main__":
    make_password_nullable()
