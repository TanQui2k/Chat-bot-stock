from collections.abc import Generator
from typing import Optional

from fastapi import Cookie, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from src.core.database import SessionLocal
from src.core.security import verify_token
from src.crud.crud_user import get_user
from src.services.token_blacklist import is_token_blacklisted


def get_db() -> Generator[Session, None, None]:
    """Provide one database session per API request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _access_token(authorization: Optional[str], cookie_token: Optional[str]) -> Optional[str]:
    if authorization:
        return authorization[7:] if authorization.startswith("Bearer ") else authorization
    return cookie_token


async def get_current_user(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    """Return the authenticated user from a bearer header or auth cookie."""
    token = _access_token(authorization, access_token)
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        if is_token_blacklisted(token):
            raise HTTPException(status_code=401, detail="Token has been revoked")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        user = get_user(db, user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Authentication error: {exc}") from exc


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    access_token: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    """Return the authenticated user when possible, otherwise ``None``."""
    token = _access_token(authorization, access_token)
    if not token:
        return None

    try:
        payload = verify_token(token)
        if payload is None or is_token_blacklisted(token):
            return None

        user_id = payload.get("sub")
        return get_user(db, user_id) if user_id else None
    except Exception:
        return None
