@echo off
REM Run FastAPI server with environment variables from .env
REM Usage: run_server.bat [port] [host]
REM Example: run_server.bat 8000 0.0.0.0

setlocal enabledelayedexpansion

REM Get backend directory
cd /d "%~dp0"

REM Set PYTHONPATH to include backend directory
set PYTHONPATH=%CD%

set PYTHON_CMD=python
if exist "%CD%\.venv\Scripts\python.exe" (
    set PYTHON_CMD=%CD%\.venv\Scripts\python.exe
)

REM Run the FastAPI server
echo Starting FastAPI server...
echo.

%PYTHON_CMD% run.py

pause
