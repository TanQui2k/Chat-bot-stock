from typing import List, Optional
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict

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


class ChatTurnRequest(BaseModel):
    content: str


class ChatTurnResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse

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
