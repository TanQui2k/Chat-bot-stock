from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, Field, validator

# ==========================================
# User Schemas
# ==========================================
class UserBase(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: Optional[str] = None
    phone_number: Optional[str] = None

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    phone_number: Optional[str] = None
    phone_verified: bool = False
    google_id: Optional[str] = None
    auth_providers: List[str] = []
    default_auth_method: str = "password"
    created_at: datetime
    last_login: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
    
User = UserResponse

# ==========================================
# Authentication Schemas
# ==========================================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class TokenPayload(BaseModel):
    sub: Optional[str] = None  # User ID
    auth_method: str = "password"
    phone_verified: bool = False

class PhoneVerificationRequest(BaseModel):
    phone_number: str = Field(..., pattern=r'^(\+84|0|84)[0-9]{9,10}$')

class PhoneVerificationVerify(BaseModel):
    phone_number: str
    verification_code: str

class GoogleLoginRequest(BaseModel):
    access_token: str = Field(..., description="Google OAuth2 access token from frontend")

class LoginRequest(BaseModel):
    identifier: str = Field(..., description="Username, email, or phone number")
    password: str

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class AuthMethodResponse(BaseModel):
    phone: bool = False
    google: bool = False
    password: bool = False