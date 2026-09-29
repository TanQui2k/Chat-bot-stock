$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "Backend virtual environment is missing. Run .\scripts\setup.ps1 first."
}

Push-Location $backendDir
try {
    & $pythonExe scripts\daily_update.py
    if ($LASTEXITCODE -ne 0) { throw "Stock data update failed." }
}
finally {
    Pop-Location
}
