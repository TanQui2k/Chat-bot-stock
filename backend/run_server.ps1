# Run FastAPI server with settings from .env file

# Set current directory to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommandPath
Set-Location $scriptPath

# Set PYTHONPATH
$env:PYTHONPATH = $scriptPath

Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host ""

# Run the Python script
python run.py
