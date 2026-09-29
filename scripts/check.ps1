param(
    [switch]$SkipBuild
)

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $projectRoot "backend"
$frontendDir = Join-Path $projectRoot "frontend"
$pythonExe = Join-Path $backendDir ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $pythonExe)) {
    throw "Backend virtual environment is missing. Run .\scripts\setup.ps1 first."
}

Write-Host "[1/4] Checking Python dependencies..." -ForegroundColor Cyan
& $pythonExe -m pip check
if ($LASTEXITCODE -ne 0) { throw "Python dependency check failed." }

Write-Host "[2/4] Running backend tests..." -ForegroundColor Cyan
Push-Location $backendDir
try {
    & $pythonExe -m unittest discover -s tests -p "test_*.py" -v
    if ($LASTEXITCODE -ne 0) { throw "Backend tests failed." }
}
finally {
    Pop-Location
}

Write-Host "[3/4] Running frontend lint..." -ForegroundColor Cyan
Push-Location $frontendDir
try {
    npm run lint
    if ($LASTEXITCODE -ne 0) { throw "Frontend lint failed." }

    if (-not $SkipBuild) {
        Write-Host "[4/4] Building frontend..." -ForegroundColor Cyan
        npm run build
        if ($LASTEXITCODE -ne 0) { throw "Frontend build failed." }
    }
    else {
        Write-Host "[4/4] Frontend build skipped." -ForegroundColor DarkYellow
    }
}
finally {
    Pop-Location
}

Write-Host "All checks passed." -ForegroundColor Green
