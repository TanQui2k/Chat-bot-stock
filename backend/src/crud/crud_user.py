from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import secrets
import re
from typing import List, Optional
from uuid import UUID
from src.models.user import User, PhoneNumberVerification
from src.schemas.user_schema import UserCreate, UserUpdate
from src.core.security import get_password_hash, verify_password

# ==========================================
# User CRUD Operations
# ==========================================

def get_user(db: Session, user_id: UUID) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()

def get_user_by_phone(db: Session, phone_number: str) -> Optional[User]:
    return db.query(User).filter(User.phone_number == phone_number).first()

def get_user_by_google_id(db: Session, google_id: str) -> Optional[User]:
    return db.query(User).filter(User.google_id == google_id).first()

def get_user_by_identifier(db: Session, identifier: str) -> Optional[User]:
    """Get user by email, phone, or username"""
    # Try phone number (Vietnamese format: +84, 0, 84)
    phone_pattern = r'^(\+84|0|84)[0-9]{9,10}$'
    if re.match(phone_pattern, identifier):
        return db.query(User).filter(User.phone_number == identifier).first()
    
    # Try email
    if '@' in identifier:
        return db.query(User).filter(User.email == identifier).first()
    
    # Try username
    return db.query(User).filter(User.username == identifier).first()

def create_user(db: Session, user: UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        auth_providers=["password"]
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_from_google(db: Session, google_info: dict) -> User:
    """Create or get user from Google OAuth"""
    # Check if user already exists by google_id
    existing_user = get_user_by_google_id(db, google_info.get("google_id"))
    if existing_user:
        existing_user.last_login = datetime.now()
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # Check if user exists by email
    existing_email_user = get_user_by_email(db, google_info.get("email"))
    if existing_email_user:
        # Link Google account to existing user
        existing_email_user.google_id = google_info.get("google_id")
        existing_email_user.auth_providers = list(set(existing_email_user.auth_providers or []) | {"google"})
        existing_email_user.full_name = google_info.get("full_name")
        existing_email_user.avatar_url = google_info.get("avatar_url")
        existing_email_user.last_login = datetime.now()
        db.commit()
        db.refresh(existing_email_user)
        return existing_email_user
    
    # Create new user
    full_name = google_info.get("full_name", "")
    email = google_info.get("email", "")
    
    # Derive username from full_name or email prefix
    if full_name:
        # Lowercase and remove spaces
        base_username = re.sub(r'[^a-zA-Z0-9]', '', full_name).lower()
    else:
        base_username = email.split("@")[0]
        
    # Ensure uniqueness
    username = base_username
    counter = 1
    while db.query(User).filter(User.username == username).first():
        username = f"{base_username}{counter}"
        counter += 1

    db_user = User(
        username=username,
        email=email,
        google_id=google_info.get("google_id"),
        full_name=full_name,
        avatar_url=google_info.get("avatar_url"),
        phone_verified=True,
        auth_providers=["google"],
        default_auth_method="google"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_from_phone(db: Session, phone_number: str, user_data: dict) -> User:
    """Create or get user from phone verification"""
    # Check if user already exists by phone
    existing_user = get_user_by_phone(db, phone_number)
    if existing_user:
        if "phone" not in (existing_user.auth_providers or []):
            existing_user.auth_providers = list(set(existing_user.auth_providers or []) | {"phone"})
            existing_user.phone_verified = True
            existing_user.last_login = datetime.now()
        else:
            existing_user.last_login = datetime.now()
        db.commit()
        db.refresh(existing_user)
        return existing_user
    
    # Create new user
    db_user = User(
        username=user_data.get("username", phone_number),
        email=user_data.get("email"),
        phone_number=phone_number,
        phone_verified=True,
        full_name=user_data.get("full_name"),
        auth_providers=["phone"],
        default_auth_method="phone"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password_login(db: Session, identifier: str, password: str) -> Optional[User]:
    """Verify user credentials for password login"""
    user = get_user_by_identifier(db, identifier)
    if not user:
        return None
    if not user.hashed_password:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# ==========================================
# Phone Verification CRUD Operations
# ==========================================

def create_phone_verification(db: Session, phone_number: str) -> PhoneNumberVerification:
    """Create a new phone verification code"""
    # Generate 6-digit code
    code = secrets.token_hex(3)  # 6 hex characters
    expires_at = datetime.now() + timedelta(minutes=10)
    
    verification = PhoneNumberVerification(
        phone_number=phone_number,
        verification_code=code,
        expires_at=expires_at
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)
    return verification

def verify_phone_code(db: Session, phone_number: str, code: str) -> bool:
    """Verify phone code and mark as used"""
    # Find the most recent verification for this phone number
    verification = db.query(PhoneNumberVerification)\
        .filter(
            PhoneNumberVerification.phone_number == phone_number,
            PhoneNumberVerification.verification_code == code,
            PhoneNumberVerification.is_used == False,
            PhoneNumberVerification.expires_at > datetime.now()
        )\
        .order_by(desc(PhoneNumberVerification.created_at))\
        .first()
    
    if not verification:
        return False
    
    # Mark as used
    verification.is_used = True
    db.commit()
    return True

def get_user_auth_methods(db: Session, user_id: UUID) -> dict:
    """Get available authentication methods for a user"""
    user = get_user(db, user_id)
    if not user:
        return {}
    
    return {
        "phone": "phone" in (user.auth_providers or []),
        "google": "google" in (user.auth_providers or []),
        "password": bool(user.hashed_password)
    }