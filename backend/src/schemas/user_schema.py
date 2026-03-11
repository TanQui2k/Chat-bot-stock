from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict

# ==========================================
# User Schemas
# ==========================================
class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Chat Message Schemas
# ==========================================
class MessageBase(BaseModel):
    role: str
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    session_id: UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# ==========================================
# Chat Session Schemas
# ==========================================
class SessionBase(BaseModel):
    title: Optional[str] = "New Chat"

class SessionCreate(SessionBase):
    user_id: UUID

class SessionResponse(SessionBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    messages: List[MessageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
