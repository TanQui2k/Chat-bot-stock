from sqlalchemy.orm import Session
from src.models.user import ChatSession, ChatMessage
from src.schemas.chat_schema import SessionCreate, MessageCreate
from uuid import UUID
import unicodedata

def get_sessions(db: Session, user_id: UUID):
    return db.query(ChatSession).filter(ChatSession.user_id == user_id).all()

from src.models.user import User

def create_session(db: Session, session: SessionCreate):
    # Handle anonymous user requests from UI by creating a placeholder User
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        user = User(
            id=session.user_id,
            username=f"UI_{str(session.user_id)[:8]}",
            email=f"ui_{session.user_id}@chat.local",
            hashed_password="none"
        )
        db.add(user)
        db.commit()
    
    # Safe text handling for Windows db locales
    safe_title = _db_safe_text(session.title) if session.title else None
    db_session = ChatSession(user_id=session.user_id, title=safe_title)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_messages(db: Session, session_id: UUID):
    return db.query(ChatMessage).filter(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()).all()

def get_recent_messages(db: Session, session_id: UUID, limit: int = 10):
    rows = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    return list(reversed(rows))

def create_message(db: Session, session_id: UUID, message: MessageCreate):
    content = _db_safe_text(message.content)
    db_message = ChatMessage(session_id=session_id, role=message.role, content=content)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def _db_safe_text(text: str) -> str:
    """
    Best-effort: avoid crashes when DB/client encoding cannot represent some Vietnamese characters.
    If cp1258 encoding fails, strip diacritics.
    """
    if text is None:
        return ""
    try:
        text.encode("cp1258")
        return text
    except UnicodeEncodeError:
        normalized = unicodedata.normalize("NFKD", text)
        stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
        return stripped
