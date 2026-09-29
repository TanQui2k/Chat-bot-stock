param(
    [switch]$SkipDatabase
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"
$pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"

Write-Host "[1/4] Preparing backend environment..." -ForegroundColor Cyan
if (-not (Test-Path -LiteralPath $pythonExe)) {
    python -m venv (Join-Path $backendDir ".venv")
    if ($LASTEXITCODE -ne 0) { throw "Could not create backend virtual environment." }
}

if (-not (Test-Path -LiteralPath (Join-Path $backendDir ".env"))) {
    Copy-Item -LiteralPath (Join-Path $backendDir ".env.example") -Destination (Join-Path $backendDir ".env")
}

& $pythonExe -m pip install -r (Join-Path $backendDir "requirements.txt")
if ($LASTEXITCODE -ne 0) { throw "Backend dependency installation failed." }

Write-Host "[2/4] Preparing frontend environment..." -ForegroundColor Cyan
if (-not (Test-Path -LiteralPath (Join-Path $frontendDir ".env.local"))) {
    Copy-Item -LiteralPath (Join-Path $frontendDir ".env.example") -Destination (Join-Path $frontendDir ".env.local")
}

Push-Location $frontendDir
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw "Frontend dependency installation failed." }
}
finally {
    Pop-Location
}

if (-not $SkipDatabase) {
    Write-Host "[3/4] Starting local PostgreSQL..." -ForegroundColor Cyan
    & (Join-Path $backendDir "run_local_db.ps1")
    if ($LASTEXITCODE -ne 0) { throw "Local PostgreSQL setup failed." }

    Write-Host "[4/4] Applying database migrations..." -ForegroundColor Cyan
    Push-Location $backendDir
    try {
        & $pythonExe -m alembic upgrade head
        if ($LASTEXITCODE -ne 0) { throw "Database migration failed." }
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Host "[3/4] Database setup skipped." -ForegroundColor DarkYellow
    Write-Host "[4/4] Database migrations skipped." -ForegroundColor DarkYellow
}

Write-Host "Setup completed." -ForegroundColor Green
