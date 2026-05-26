from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.api.dependencies import get_current_user, get_db
from src.crud import crud_chat
from src.schemas.chat_schema import (
    ChatTurnRequest,
    ChatTurnResponse,
    MessageCreate,
    MessageResponse,
    SessionCreate,
    SessionResponse,
)

router = APIRouter(prefix="/chat", tags=["chat"])


class LegacyChatRequest(BaseModel):
    message: str


class LegacyChatResponse(BaseModel):
    content: str
    timestamp: str


def _ensure_session_owner(db: Session, session_id: UUID, current_user):
    session = crud_chat.get_session(db, session_id=session_id)
    if session is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found")

    if str(session.user_id) != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this chat session")

    return session


@router.post("/message", response_model=LegacyChatResponse)
def send_message(
    payload: LegacyChatRequest,
    current_user=Depends(get_current_user),
):
    """Compatibility endpoint for older authenticated clients that send stateless chat messages."""
    user_text = (payload.message or "").strip()
    if not user_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="message is required")

    from src.services.chat_service import ChatService

    assistant_text = ChatService().route_intent(user_text, history=[])
    return LegacyChatResponse(
        content=assistant_text,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@router.post("/sessions", response_model=SessionResponse)
def create_session(
    session: SessionCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if str(session.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot create chat session for another user",
        )

    return crud_chat.create_session(db=db, session=session)


@router.get("/sessions/{user_id}", response_model=List[SessionResponse])
def get_sessions(
    user_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if str(user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot read another user's chat sessions",
        )

    return crud_chat.get_sessions(db, user_id=user_id)


@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
def create_message(
    session_id: UUID,
    message: MessageCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_session_owner(db, session_id=session_id, current_user=current_user)
    return crud_chat.create_message(db=db, session_id=session_id, message=message)


@router.post("/sessions/{session_id}/turn", response_model=ChatTurnResponse)
def chat_turn(
    session_id: UUID,
    payload: ChatTurnRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_text = (payload.content or "").strip()
    if not user_text:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="content is required")

    _ensure_session_owner(db, session_id=session_id, current_user=current_user)

    user_msg = crud_chat.create_message(
        db=db,
        session_id=session_id,
        message=MessageCreate(role="user", content=user_text),
    )

    history_rows = crud_chat.get_recent_messages(db, session_id=session_id, limit=10)
    history = [{"role": m.role, "content": m.content} for m in history_rows if m.id != user_msg.id]

    from src.services.chat_service import ChatService

    assistant_text = ChatService().route_intent(user_text, history=history)

    assistant_msg = crud_chat.create_message(
        db=db,
        session_id=session_id,
        message=MessageCreate(role="assistant", content=assistant_text),
    )

    return ChatTurnResponse(user_message=user_msg, assistant_message=assistant_msg)


@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(
    session_id: UUID,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    _ensure_session_owner(db, session_id=session_id, current_user=current_user)
    return crud_chat.get_messages(db, session_id=session_id)
