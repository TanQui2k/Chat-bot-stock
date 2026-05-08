#!/usr/bin/env python3
"""
Run the FastAPI application with settings from .env file
"""
import os
import sys
import uvicorn
from pathlib import Path
from subprocess import run

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

if __name__ == "__main__":
    print(f"Starting server on {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    print(f"API Docs: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/docs")
    
    uvicorn.run(
        "src.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )
