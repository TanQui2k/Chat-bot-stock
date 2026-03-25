from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import re

from src import schemas
from src.crud import crud_user
from src.core.security import (
    create_user_token, verify_password, get_password_hash
)
from src.api.dependencies import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

# ==========================================
# Phone Authentication
# ==========================================

@router.post("/phone/send-code")
def send_phone_verification_code(
    request: schemas.PhoneVerificationRequest,
    db: Session = Depends(get_db)
):
    """Send verification code to phone number."""
    phone_pattern = r'^(\+84|0|84)[0-9]{9,10}$'
    if not re.match(phone_pattern, request.phone_number):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format. Use: +84xxxxxxxxx or 0xxxxxxxxx"
        )
    
    # Check if phone is already registered
    existing_user = crud_user.get_user_by_phone(db, request.phone_number)
    if existing_user and "phone" in (existing_user.auth_providers or []):
        raise HTTPException(
            status_code=400,
            detail="Phone number already verified"
        )
    
    # Create verification record
    verification = crud_user.create_phone_verification(db, request.phone_number)
    
    # TODO: Send SMS with verification code
    # For demo: return code in response
    # In production: use SMS gateway (Twilio, msg91, or local provider)
    return {
        "message": "Verification code sent successfully",
        "phone_number": request.phone_number,
        "code": verification.verification_code,  # For demo only!
        "expires_in": 600  # 10 minutes in seconds
    }

@router.post("/phone/verify")
def verify_phone_code(
    request: schemas.PhoneVerificationVerify,
    db: Session = Depends(get_db)
):
    """Verify phone code and login/create user."""
    # Verify code
    is_valid = crud_user.verify_phone_code(db, request.phone_number, request.verification_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code"
        )
    
    # Get or create user
    user = crud_user.create_user_from_phone(db, request.phone_number, {
        "username": request.phone_number,
        "email": None,
        "full_name": None
    })
    
    # Create token
    token = create_user_token(
        user_id=str(user.id),
        auth_method="phone",
        phone_verified=True
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": schemas.UserResponse.model_validate(user)
    }

@router.post("/phone/verify-only")
def verify_phone_code_only(
    request: schemas.PhoneVerificationVerify,
    db: Session = Depends(get_db)
):
    """Verify phone code only (for updating existing user)."""
    is_valid = crud_user.verify_phone_code(db, request.phone_number, request.verification_code)
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification code"
        )
    
    return {"message": "Phone number verified successfully"}

# ==========================================
# Google OAuth Authentication
# ==========================================

@router.post("/google/login")
def google_login(
    request: schemas.GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """Login with Google OAuth ID token."""
    # TODO: Verify Google ID token
    # In production: use google.oauth2.id_token.verify_oauth2_token
    # For demo: simulate token verification
    
    # Simulated Google user info (replace with actual token verification)
    google_info = {
        "google_id": f"google_{request.id_token[:20]}",
        "email": f"user_{request.id_token[:10]}@gmail.com",
        "full_name": "Google User",
        "avatar_url": "https://example.com/avatar.png"
    }
    
    # Create or get user
    user = crud_user.create_user_from_google(db, google_info)
    
    # Create token
    token = create_user_token(
        user_id=str(user.id),
        auth_method="google",
        phone_verified=user.phone_verified if hasattr(user, 'phone_verified') else False
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": schemas.UserResponse.model_validate(user)
    }

@router.post("/google/link")
def link_google_account(
    request: schemas.GoogleLoginRequest,
    current_user: schemas.User = Depends(get_current_user),  # Requires authentication
    db: Session = Depends(get_db)
):
    """Link Google account to existing user."""
    # TODO: Verify Google ID token
    google_info = {
        "google_id": f"google_{request.id_token[:20]}",
        "email": f"user_{request.id_token[:10]}@gmail.com",
        "full_name": "Google User",
        "avatar_url": "https://example.com/avatar.png"
    }
    
    # Check if Google ID is already linked
    existing_user = crud_user.get_user_by_google_id(db, google_info["google_id"])
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Google account already linked to another user"
        )
    
    # Link Google account to current user
    current_user.google_id = google_info["google_id"]
    current_user.full_name = google_info.get("full_name")
    current_user.avatar_url = google_info.get("avatar_url")
    current_user.auth_providers = list(set((current_user.auth_providers or []) + ["google"]))
    db.commit()
    
    return {
        "message": "Google account linked successfully",
        "user": schemas.UserResponse.model_validate(current_user)
    }

# ==========================================
# Password Authentication (Existing)
# ==========================================

@router.post("/login")
def login(
    request: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with email/phone and password."""
    user = crud_user.verify_password_login(db, request.identifier, request.password)
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    
    # Create token
    token = create_user_token(
        user_id=str(user.id),
        auth_method="password",
        phone_verified=user.phone_verified if hasattr(user, 'phone_verified') else False
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": schemas.UserResponse.model_validate(user)
    }

@router.post("/logout")
def logout(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout current user."""
    # For JWT, logout is handled client-side by removing token
    # Add token to blacklist if needed for session invalidation
    return {"message": "Logged out successfully"}

# ==========================================
# User Profile
# ==========================================

@router.get("/profile")
def get_profile(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    return schemas.UserResponse.model_validate(current_user)

@router.get("/auth-methods")
def get_auth_methods(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available authentication methods for current user."""
    methods = crud_user.get_user_auth_methods(db, current_user.id)
    return schemas.AuthMethodResponse(**methods)

@router.post("/auth-methods/add-phone")
def add_phone_to_profile(
    request: schemas.PhoneVerificationRequest,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add phone number to existing user profile."""
    # Check if phone is already used by another user
    existing = crud_user.get_user_by_phone(db, request.phone_number)
    if existing and str(existing.id) != str(current_user.id):
        raise HTTPException(
            status_code=400,
            detail="Phone number already in use by another account"
        )
    
    # Send verification code
    verification = crud_user.create_phone_verification(db, request.phone_number)
    
    return {
        "message": "Verification code sent",
        "code": verification.verification_code,  # For demo only!
        "phone_number": request.phone_number
    }