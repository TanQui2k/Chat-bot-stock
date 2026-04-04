from src.core.config import SessionLocal
from fastapi import Depends, HTTPException, Header
from typing import Optional

def get_db():
    """Generator cung cấp session DB cho từng request API."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# Authentication Dependencies
# ==========================================

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db = Depends(get_db)
):
    """Get current authenticated user from JWT token."""
    from src.core.security import verify_token
    from src.crud.crud_user import get_user
    
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Remove "Bearer " prefix if present
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
        
        payload = verify_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Check if token has been blacklisted (user logged out)
        from src.services.token_blacklist import is_token_blacklisted
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
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication error: {str(e)}")

async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db = Depends(get_db)
):
    """Get current user if authenticated, otherwise return None."""
    from src.core.security import verify_token
    from src.crud.crud_user import get_user
    
    if not authorization:
        return None
    
    try:
        # Remove "Bearer " prefix if present
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
        
        payload = verify_token(token)
        if payload is None:
            return None
        
        # Check blacklist
        from src.services.token_blacklist import is_token_blacklisted
        if is_token_blacklisted(token):
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        user = get_user(db, user_id)
        return user
    except Exception:
        return None