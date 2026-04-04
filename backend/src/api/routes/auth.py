from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import re
import logging

logger = logging.getLogger(__name__)

# Shared phone validation pattern
PHONE_PATTERN = re.compile(r'^(\+84|0|84)[0-9]{9,10}$')

from src import schemas
from src.crud import crud_user
from src.core.security import (
    create_user_token, verify_password, get_password_hash
)
from src.api.dependencies import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

# Helpers
def set_auth_cookie(response: JSONResponse, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,  # Set to True in production
        samesite="strict",
        max_age=60 * 24 * 60  # 24 hours
    )

# ==========================================
# Phone Authentication
# ==========================================

@router.post("/phone/send-code")
def send_phone_verification_code(
    request: schemas.PhoneVerificationRequest,
    db: Session = Depends(get_db)
):
    """Send verification code to phone number."""
    if not PHONE_PATTERN.match(request.phone_number):
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
    
    # [DEV] Log code to console
    logger.info(f"[DEV] OTP for {request.phone_number}: {verification.verification_code}")
    
    return {
        "message": "Verification code sent successfully",
        "phone_number": request.phone_number,
        "expires_in": 600
    }

@router.post("/phone/verify")
def verify_phone_code(
    request: schemas.PhoneVerificationVerify,
    db: Session = Depends(get_db)
):
    """Verify phone code and login/create user."""
    is_valid = crud_user.verify_phone_code(db, request.phone_number, request.verification_code)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    
    user = crud_user.create_user_from_phone(db, request.phone_number, {
        "username": request.phone_number
    })
    
    token = create_user_token(user_id=str(user.id), auth_method="phone", phone_verified=True)
    
    response = JSONResponse(content={
        "message": "Login successful",
        "user": schemas.UserResponse.model_validate(user).model_dump(mode='json')
    })
    set_auth_cookie(response, token)
    return response

# ==========================================
# Google OAuth Authentication
# ==========================================

@router.post("/google/login")
async def google_login(
    request: schemas.GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    """Login with Google OAuth access token."""
    from src.services.google_auth_service import verify_google_access_token, GoogleAuthError
    
    try:
        google_user = await verify_google_access_token(request.access_token)
    except GoogleAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))
    
    user = crud_user.create_user_from_google(db, google_user.to_dict())
    
    token = create_user_token(
        user_id=str(user.id),
        auth_method="google",
        phone_verified=user.phone_verified if hasattr(user, 'phone_verified') else False
    )
    
    response = JSONResponse(content={
        "message": "Google login successful",
        "user": schemas.UserResponse.model_validate(user).model_dump(mode='json')
    })
    set_auth_cookie(response, token)
    return response

# ==========================================
# Password Authentication
# ==========================================

@router.post("/register")
def register(
    request: schemas.UserRegister,
    db: Session = Depends(get_db)
):
    """Register a new user with email and password."""
    # Check if user already exists
    existing_user = crud_user.get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = crud_user.create_user(
        db, 
        email=request.email, 
        password=request.password, 
        full_name=request.full_name
    )
    
    token = create_user_token(user_id=str(user.id), auth_method="password")
    
    response = JSONResponse(content={
        "message": "Registration successful",
        "user": schemas.UserResponse.model_validate(user).model_dump(mode='json')
    }, status_code=status.HTTP_201_CREATED)
    
    set_auth_cookie(response, token)
    return response

@router.post("/login")
def login(
    request: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with email/phone and password."""
    user = crud_user.verify_password_login(db, request.identifier, request.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    
    token = create_user_token(
        user_id=str(user.id),
        auth_method="password",
        phone_verified=user.phone_verified if hasattr(user, 'phone_verified') else False
    )
    
    response = JSONResponse(content={
        "message": "Login successful",
        "user": schemas.UserResponse.model_validate(user).model_dump(mode='json')
    })
    set_auth_cookie(response, token)
    return response

@router.post("/logout")
def logout(
    authorization: str = Depends(lambda authorization=Header(None): authorization),
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Logout current user and invalidate JWT token."""
    from src.services.token_blacklist import blacklist_token
    
    if authorization:
        token = authorization[7:] if authorization.startswith("Bearer ") else authorization
        blacklist_token(token)
    
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
    logger.info(f"[DEV] OTP for {request.phone_number}: {verification.verification_code}")
    
    return {
        "message": "Verification code sent",
        "phone_number": request.phone_number
    }