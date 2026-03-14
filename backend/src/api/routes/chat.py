from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from src.api.dependencies import get_db
from src.crud import crud_chat
from src.schemas.chat_schema import SessionCreate, SessionResponse, MessageCreate, MessageResponse

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/sessions", response_model=SessionResponse)
def create_session(session: SessionCreate, db: Session = Depends(get_db)):
    return crud_chat.create_session(db=db, session=session)

@router.get("/sessions/{user_id}", response_model=List[SessionResponse])
def get_sessions(user_id: UUID, db: Session = Depends(get_db)):
    return crud_chat.get_sessions(db, user_id=user_id)

@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
def create_message(session_id: UUID, message: MessageCreate, db: Session = Depends(get_db)):
    return crud_chat.create_message(db=db, session_id=session_id, message=message)

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(session_id: UUID, db: Session = Depends(get_db)):
    return crud_chat.get_messages(db, session_id=session_id)
