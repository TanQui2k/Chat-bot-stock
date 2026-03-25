"""Script to add authentication columns to users table."""

from sqlalchemy import text, Column, String, Boolean, DateTime, JSON
from sqlalchemy.orm import sessionmaker
from src.core.config import engine
from src.models.user import User, PhoneNumberVerification

def add_auth_columns():
    """Add authentication-related columns to users table."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Add phone_number column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20)
        """))
        print("Added phone_number column")
        
        # Add phone_verified column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE
        """))
        print("Added phone_verified column")
        
        # Add google_id column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS google_id VARCHAR(255)
        """))
        print("Added google_id column")
        
        # Add auth_providers column (JSON type)
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS auth_providers JSON DEFAULT '[]'
        """))
        print("Added auth_providers column")
        
        # Add default_auth_method column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS default_auth_method VARCHAR(20) DEFAULT 'password'
        """))
        print("Added default_auth_method column")
        
        # Add full_name column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS full_name VARCHAR(255)
        """))
        print("Added full_name column")
        
        # Add avatar_url column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500)
        """))
        print("Added avatar_url column")
        
        # Add last_login column
        db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE
        """))
        print("Added last_login column")
        
        # Create phone_verifications table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS phone_verifications (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20) NOT NULL,
                verification_code VARCHAR(6) NOT NULL,
                is_used BOOLEAN DEFAULT FALSE,
                expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        """))
        print("Created phone_verifications table")
        
        # Create indexes for better query performance
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number)
        """))
        print("Created index on users.phone_number")
        
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id)
        """))
        print("Created index on users.google_id")
        
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_phone_verifications_phone ON phone_verifications(phone_number)
        """))
        print("Created index on phone_verifications.phone_number")
        
        db.commit()
        print("\n✓ All columns added successfully!")
        print("✓ Database migration completed!")
        
    except Exception as e:
        db.rollback()
        print(f"Error: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting database migration for authentication...")
    print("=" * 50)
    add_auth_columns()
    print("=" * 50)
    print("Migration completed!")