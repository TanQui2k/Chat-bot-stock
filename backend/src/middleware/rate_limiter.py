"""
Rate limiter middleware for sensitive API endpoints.

Uses an in-memory sliding-window counter. This is appropriate for a single
backend instance. Use Redis or another shared store for multi-instance deploys.
"""

import logging
import threading
import time
from collections import defaultdict
from typing import Optional

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from src.core.config import settings

logger = logging.getLogger(__name__)

_rate_store: dict[str, list[float]] = defaultdict(list)
_lock = threading.Lock()
_request_count = 0


class RateLimitConfig:
    """Configuration for a rate-limited endpoint."""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds


RATE_LIMIT_RULES: dict[str, RateLimitConfig] = {
    "/api/auth/phone/send-code": RateLimitConfig(max_requests=5, window_seconds=60),
    "/api/auth/login": RateLimitConfig(max_requests=10, window_seconds=60),
    "/api/auth/google/login": RateLimitConfig(max_requests=10, window_seconds=60),
    "/api/auth/phone/verify": RateLimitConfig(max_requests=10, window_seconds=60),
}


def _get_client_ip(request: Request) -> str:
    """Extract client IP. Only trust proxy headers when explicitly enabled."""
    forwarded = request.headers.get("X-Forwarded-For") if settings.TRUST_PROXY_HEADERS else None
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _check_rate_limit(key: str, config: RateLimitConfig) -> tuple[bool, int]:
    now = time.time()
    window_start = now - config.window_seconds

    with _lock:
        _rate_store[key] = [ts for ts in _rate_store[key] if ts > window_start]
        current_count = len(_rate_store[key])

        if current_count >= config.max_requests:
            return False, 0

        _rate_store[key].append(now)
        return True, config.max_requests - current_count - 1


def _cleanup_old_entries():
    """Periodically clean up stale entries to prevent memory leaks."""
    now = time.time()
    max_window = max(r.window_seconds for r in RATE_LIMIT_RULES.values()) if RATE_LIMIT_RULES else 60
    cutoff = now - max_window

    with _lock:
        empty_keys = []
        for key, timestamps in _rate_store.items():
            _rate_store[key] = [ts for ts in timestamps if ts > cutoff]
            if not _rate_store[key]:
                empty_keys.append(key)
        for key in empty_keys:
            del _rate_store[key]


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware that enforces rate limits on configured endpoints."""

    async def dispatch(self, request: Request, call_next):
        global _request_count

        path = request.url.path
        config: Optional[RateLimitConfig] = None
        for rule_path, rule_config in RATE_LIMIT_RULES.items():
            if path == rule_path or path.startswith(rule_path):
                config = rule_config
                break

        if config is None:
            return await call_next(request)

        client_ip = _get_client_ip(request)
        rate_key = f"{path}:{client_ip}"

        allowed, remaining = _check_rate_limit(rate_key, config)

        if not allowed:
            logger.warning("Rate limit exceeded: %s", rate_key)
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Quá nhiều yêu cầu. Vui lòng thử lại sau.",
                    "retry_after": config.window_seconds,
                },
                headers={
                    "Retry-After": str(config.window_seconds),
                    "X-RateLimit-Limit": str(config.max_requests),
                    "X-RateLimit-Remaining": "0",
                },
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(config.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

        _request_count += 1
        if _request_count % 500 == 0:
            _cleanup_old_entries()

        return response
