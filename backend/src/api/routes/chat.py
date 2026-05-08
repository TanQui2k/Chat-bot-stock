from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from src.api.dependencies import get_db
from src.crud import crud_chat
from src.schemas.chat_schema import (
    SessionCreate,
    SessionResponse,
    MessageCreate,
    MessageResponse,
    ChatTurnRequest,
    ChatTurnResponse,
)
from src.services.vnstock_service import VnStockPriceService
from src.services.llm_service import LLMService
from src.utils.helpers import format_context_for_llm
import re

router = APIRouter(prefix="/chat", tags=["chat"])


class LegacyChatRequest(BaseModel):
    message: str


class LegacyChatResponse(BaseModel):
    content: str
    timestamp: str


@router.post("/message", response_model=LegacyChatResponse)
def send_message(payload: LegacyChatRequest):
    """Compatibility endpoint for older frontend clients that send stateless chat messages."""
    user_text = (payload.message or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="message is required")

    from src.services.chat_service import ChatService

    assistant_text = ChatService().route_intent(user_text, history=[])
    return LegacyChatResponse(
        content=assistant_text,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

@router.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    return crud_chat.create_session(db=db, session=session)

@router.get("/sessions/{user_id}", response_model=List[SessionResponse])
def get_sessions(user_id: UUID, db: Session = Depends(get_db)):
    return crud_chat.get_sessions(db, user_id=user_id)

@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
def create_message(session_id: UUID, message: MessageCreate, db: Session = Depends(get_db)):
    return crud_chat.create_message(db=db, session_id=session_id, message=message)

@router.post("/sessions/{session_id}/turn", response_model=ChatTurnResponse)
def chat_turn(session_id: UUID, payload: ChatTurnRequest, db: Session = Depends(get_db)):
    """
    One chat turn: store user message, then generate & store assistant reply.
    """
    user_text = (payload.content or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="content is required")

    # 1. Store user message
    user_msg = crud_chat.create_message(
        db=db,
        session_id=session_id,
        message=MessageCreate(role="user", content=user_text),
    )

    # 2. Get conversational history
    history_rows = crud_chat.get_recent_messages(db, session_id=session_id, limit=10)
    history = [{"role": m.role, "content": m.content} for m in history_rows if m.id != user_msg.id]

    # 3. Process intention and get AI response via ChatService
    from src.services.chat_service import ChatService
    chat_service = ChatService()
    assistant_text = chat_service.route_intent(user_text, history=history)

    # 4. Store assistant message
    assistant_msg = crud_chat.create_message(
        db=db,
        session_id=session_id,
        message=MessageCreate(role="assistant", content=assistant_text),
    )

    return ChatTurnResponse(user_message=user_msg, assistant_message=assistant_msg)

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(session_id: UUID, db: Session = Depends(get_db)):
    return crud_chat.get_messages(db, session_id=session_id)

