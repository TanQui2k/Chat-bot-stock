from fastapi import APIRouter, Depends, HTTPException
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
    Currently supports intent: hỏi giá (price) via vnstock + OpenAI natural answer.
    """
    user_text = (payload.content or "").strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="content is required")

    user_msg = crud_chat.create_message(
        db=db,
        session_id=session_id,
        message=MessageCreate(role="user", content=user_text),
    )

    history_rows = crud_chat.get_recent_messages(db, session_id=session_id, limit=10)
    history = [{"role": m.role, "content": m.content} for m in history_rows if m.id != user_msg.id]

    assistant_text = _route_intent(user_text, history=history)
    assistant_msg = crud_chat.create_message(
        db=db,
        session_id=session_id,
        message=MessageCreate(role="assistant", content=assistant_text),
    )

    return ChatTurnResponse(user_message=user_msg, assistant_message=assistant_msg)

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
def get_messages(session_id: UUID, db: Session = Depends(get_db)):
    return crud_chat.get_messages(db, session_id=session_id)


_PRICE_KW = re.compile(r"(giá|bao\s*nhiêu|price)", re.IGNORECASE)
_TICKER_RE = re.compile(r"\b([A-Za-z]{3,5})\b")


def _route_intent(user_text: str, *, history: list[dict[str, str]] | None = None) -> str:
    # Build structured context from helpers
    structured_context = format_context_for_llm(user_text, history)
    
    # Price intent
    if _PRICE_KW.search(user_text):
        return _handle_price_intent(user_text, history=history, structured_context=structured_context)

    # Default: use OpenAI for natural reply with full structured context.
    try:
        ans = LLMService().natural_chat_answer(
            question=user_text,
            history=history,
            structured_context=structured_context
        )
        return ans or "Mình đã nhận câu hỏi của bạn. Bạn có thể hỏi theo dạng: 'Giá FPT bao nhiêu?'."
    except Exception:
        return "Mình đã nhận câu hỏi của bạn. Bạn có thể hỏi theo dạng: 'Giá FPT bao nhiêu?'."

def _handle_price_intent(
    user_text: str, 
    *, 
    history: list[dict[str, str]] | None = None,
    structured_context: str | None = None
) -> str:
    m = _TICKER_RE.search(user_text)
    if not m:
        return "Bạn cho mình xin mã cổ phiếu (VD: FPT, VCB) để mình báo giá nhé."

    symbol = m.group(1).upper()
    price_info = VnStockPriceService().get_latest_price(symbol)

    try:
        # Build price context with structured context from ContextBuilder
        price_context = [
            f"Mã: {price_info.symbol}",
            f"Giá: {price_info.price} {price_info.currency}",
            *( [f"Thời điểm: {price_info.as_of}"] if price_info.as_of else [] ),
        ]
        
        # Combine price context with structured context
        full_context = price_context + [structured_context] if structured_context else price_context
        
        return LLMService().natural_chat_answer(
            question=user_text,
            history=history,
            context=full_context
        )
    except Exception:
        return f"Giá {price_info.symbol} hiện tại khoảng {price_info.price} {price_info.currency}."
