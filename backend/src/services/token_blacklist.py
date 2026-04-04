"""
Token Blacklist Service — Quản lý vô hiệu hóa JWT tokens khi đăng xuất.

Sử dụng in-memory set cho hiệu suất cao. Tokens tự động bị xóa khi hết hạn
để tránh rò rỉ bộ nhớ. Phù hợp cho ứng dụng single-instance.

Lưu ý: Nếu triển khai multi-instance (nhiều server), cần chuyển sang Redis.
"""

import threading
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from jose import jwt, JWTError
from src.core.config import settings

logger = logging.getLogger(__name__)

# In-memory blacklist: {jti_or_token_hash: expiry_timestamp}
_blacklist: dict[str, float] = {}
_lock = threading.Lock()


def _get_token_key(token: str) -> str:
    """Extract a unique key from the token (use 'jti' claim if available, else hash)."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"],
            options={"verify_exp": False}  # We still need to read expired tokens for blacklisting
        )
        # Use 'sub' + 'iat' as unique identifier since we don't have 'jti'
        sub = payload.get("sub", "")
        iat = payload.get("iat", 0)
        return f"{sub}:{iat}"
    except JWTError:
        # Fallback: use last 32 chars of token as key
        return token[-32:]


def _get_token_expiry(token: str) -> float:
    """Extract expiry timestamp from token."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"],
            options={"verify_exp": False}
        )
        exp = payload.get("exp", 0)
        if isinstance(exp, (int, float)):
            return float(exp)
        return 0.0
    except JWTError:
        return 0.0


def blacklist_token(token: str) -> None:
    """Add a token to the blacklist. It will be auto-cleaned when expired."""
    key = _get_token_key(token)
    expiry = _get_token_expiry(token)
    
    with _lock:
        _blacklist[key] = expiry
    
    logger.info(f"Token blacklisted: {key[:20]}...")
    
    # Cleanup expired entries periodically (every 100 additions)
    if len(_blacklist) % 100 == 0:
        _cleanup_expired()


def is_token_blacklisted(token: str) -> bool:
    """Check if a token has been blacklisted (i.e., user has logged out)."""
    key = _get_token_key(token)
    
    with _lock:
        if key in _blacklist:
            # Also verify it hasn't expired naturally (cleanup)
            expiry = _blacklist[key]
            now = datetime.now(timezone.utc).timestamp()
            if expiry > 0 and now > expiry:
                # Token has expired naturally, remove from blacklist
                del _blacklist[key]
                return False
            return True
    return False


def _cleanup_expired() -> None:
    """Remove expired tokens from blacklist to prevent memory leak."""
    now = datetime.now(timezone.utc).timestamp()
    with _lock:
        expired_keys = [k for k, exp in _blacklist.items() if exp > 0 and now > exp]
        for key in expired_keys:
            del _blacklist[key]
    
    if expired_keys:
        logger.info(f"Cleaned up {len(expired_keys)} expired tokens from blacklist")


def get_blacklist_size() -> int:
    """Return current blacklist size (for monitoring)."""
    return len(_blacklist)
