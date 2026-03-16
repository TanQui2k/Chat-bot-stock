from __future__ import annotations

import argparse
import json
import os
import sys
import uuid

import httpx


def _ensure_import_path() -> None:
    """
    Allow running the script from anywhere by adding backend/ to sys.path
    so `import src...` works.
    """
    here = os.path.abspath(os.path.dirname(__file__))
    backend_dir = os.path.abspath(os.path.join(here, ".."))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)


def ensure_test_user_id() -> str:
    """
    Create a test user directly in DB if needed (so chat_sessions FK(user_id) passes).
    Best-effort: create tables if they don't exist.
    """
    _ensure_import_path()
    try:
        from src.core.config import SessionLocal, engine  # type: ignore
        from src.models.base import Base  # type: ignore
        from src.models.user import User  # type: ignore
    except Exception as e:
        raise RuntimeError("Cannot import backend modules. Run this script from backend/ or ensure PYTHONPATH.") from e

    Base.metadata.create_all(bind=engine)

    user_id = uuid.uuid4()
    username = f"smoke_{user_id.hex[:8]}"
    email = f"{username}@example.com"

    db = SessionLocal()
    try:
        u = User(id=user_id, username=username, email=email, hashed_password="smoke_test")  # type: ignore
        db.add(u)
        db.commit()
        return str(user_id)
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test for chat /turn endpoint")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="FastAPI base URL")
    parser.add_argument("--ticker", default="FPT", help="Ticker to ask price for (3-5 letters)")
    parser.add_argument("--user-id", default=None, help="Existing user_id UUID in DB (optional). If omitted, script creates a test user.")
    args = parser.parse_args()

    base = args.base_url.rstrip("/")
    user_id = args.user_id or ensure_test_user_id()

    with httpx.Client(timeout=30) as client:
        # 1) Create session
        sess_resp = client.post(
            f"{base}/api/chat/sessions",
            json={"user_id": user_id, "title": "Smoke test"},
        )
        sess_resp.raise_for_status()
        session = sess_resp.json()
        session_id = session["id"]

        # 2) Ask price via /turn
        question = f"Giá {args.ticker} hôm nay bao nhiêu?"
        turn_resp = client.post(
            f"{base}/api/chat/sessions/{session_id}/turn",
            json={"content": question},
        )
        turn_resp.raise_for_status()
        turn = turn_resp.json()

    # Basic assertions
    assert turn["user_message"]["role"] == "user"
    assert question in turn["user_message"]["content"]
    assert turn["assistant_message"]["role"] == "assistant"
    assert isinstance(turn["assistant_message"]["content"], str) and turn["assistant_message"]["content"].strip()

    print("OK: /turn works")
    print(json.dumps({"session_id": session_id, "turn": turn}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except httpx.HTTPError as e:
        print(f"HTTP error: {e}", file=sys.stderr)
        raise
    except AssertionError as e:
        print(f"Assertion failed: {e}", file=sys.stderr)
        raise

