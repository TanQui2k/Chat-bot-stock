# Run FastAPI server with settings from .env file

# Set current directory to script directory
$scriptPath = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommandPath }
Set-Location $scriptPath

# Set PYTHONPATH
$env:PYTHONPATH = $scriptPath
$pythonExe = Join-Path $scriptPath ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Write-Host "Ensuring local PostgreSQL is running..." -ForegroundColor Green
& (Join-Path $scriptPath "run_local_db.ps1")
Write-Host ""

Write-Host "Starting FastAPI server..." -ForegroundColor Green
Write-Host ""

# Run the Python script
& $pythonExe run.py
