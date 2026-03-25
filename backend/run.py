#!/usr/bin/env python3
"""
Run the FastAPI application with settings from .env file
"""
import os
import sys
import uvicorn
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.core.config import settings

if __name__ == "__main__":
    print(f"🚀 Starting server on {settings.SERVER_HOST}:{settings.SERVER_PORT}")
    print(f"📖 API Docs: http://{settings.SERVER_HOST}:{settings.SERVER_PORT}/docs")
    
    uvicorn.run(
        "src.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True
    )
