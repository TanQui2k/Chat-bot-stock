#!/usr/bin/env python3
"""
Run the FastAPI application with settings from .env file
"""
import os
import socket
import sys
import uvicorn
from pathlib import Path
from subprocess import TimeoutExpired, run
from urllib.parse import urlparse

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

expected_python = backend_dir / ".venv" / "Scripts" / "python.exe"
current_python = Path(sys.executable).resolve()

if expected_python.exists() and current_python != expected_python.resolve():
    print(f"Switching backend runtime to {expected_python}")
    result = run([str(expected_python), __file__, *sys.argv[1:]], check=False)
    raise SystemExit(result.returncode)

from src.core.config import settings


def _local_db_target(database_url: str) -> tuple[str, int] | None:
    parsed = urlparse(database_url)
    host = parsed.hostname
    port = parsed.port or 5432
    if host in {"localhost", "127.0.0.1"} and port == 5433:
        return host, port
    return None


def _can_connect(host: str, port: int, timeout: float = 1.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _ensure_local_db() -> None:
    if not settings.AUTO_START_LOCAL_DB:
        return

    if settings.ENVIRONMENT.lower() == "production":
        return

    target = _local_db_target(settings.DATABASE_URL)
    if target is None:
        return

    host, port = target
    if _can_connect(host, port):
        print(f"Local PostgreSQL already running at {host}:{port}")
        return

    script = backend_dir / "run_local_db.ps1"
    if os.name != "nt" or not script.exists():
        raise RuntimeError(
            f"Database is not reachable at {host}:{port}, and local DB auto-start "
            "is only available on Windows with backend/run_local_db.ps1."
        )

    print(f"Starting local PostgreSQL at {host}:{port}...")
    try:
        result = run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(script)],
            check=False,
            timeout=180,
        )
        if result.returncode != 0:
            raise RuntimeError(f"run_local_db.ps1 failed with exit code {result.returncode}.")
    except TimeoutExpired:
        print("run_local_db.ps1 timed out; checking whether PostgreSQL became ready...")

    if not _can_connect(host, port, timeout=3):
        raise RuntimeError(f"Local PostgreSQL did not become reachable at {host}:{port}.")

    print(f"Local PostgreSQL is ready at {host}:{port}")


if __name__ == "__main__":
    _ensure_local_db()
    print(f"Starting server on {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    print(f"API Docs: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/docs")
    
    uvicorn.run(
        "src.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )
