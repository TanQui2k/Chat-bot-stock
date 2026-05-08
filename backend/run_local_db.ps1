$scriptPath = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommandPath }
$baseDir = Join-Path $scriptPath ".local-postgres"
$dataDir = Join-Path $baseDir "data"
$logFile = Join-Path $baseDir "server.log"
$backupFile = Join-Path (Split-Path $scriptPath -Parent) "stock.backup"

$pg17Bin = "C:\Program Files\PostgreSQL\17\bin"
$pg16Bin = "C:\Program Files\PostgreSQL\16\bin"
$pgBin = if (Test-Path $pg17Bin) { $pg17Bin } elseif (Test-Path $pg16Bin) { $pg16Bin } else { $null }

if (-not $pgBin) {
    throw "PostgreSQL binaries were not found in Program Files."
}

$initdb = Join-Path $pgBin "initdb.exe"
$pgCtl = Join-Path $pgBin "pg_ctl.exe"
$pgIsReady = Join-Path $pgBin "pg_isready.exe"
$psql = Join-Path $pgBin "psql.exe"
$createdb = Join-Path $pgBin "createdb.exe"
$pgRestore = Join-Path $pgBin "pg_restore.exe"

New-Item -ItemType Directory -Force -Path $baseDir | Out-Null

if (-not (Test-Path $dataDir)) {
    Write-Host "Initializing local PostgreSQL cluster..." -ForegroundColor Yellow
    & $initdb -D $dataDir -U postgres -A trust --auth-host=trust --auth-local=trust --encoding=UTF8
    if ($LASTEXITCODE -ne 0) {
        throw "initdb failed with exit code $LASTEXITCODE."
    }
}

& $pgIsReady -h 127.0.0.1 -p 5433 -U postgres -d postgres | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Starting local PostgreSQL on 127.0.0.1:5433..." -ForegroundColor Yellow
    & $pgCtl -D $dataDir -l $logFile -o '"-p 5433 -h 127.0.0.1"' start | Out-Null
    $pgCtlExitCode = $LASTEXITCODE
    Start-Sleep -Seconds 4
    & $pgIsReady -h 127.0.0.1 -p 5433 -U postgres -d postgres | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "pg_ctl start failed with exit code $pgCtlExitCode and PostgreSQL is still not ready on port 5433."
    }
}

$dbExists = & $psql -h 127.0.0.1 -p 5433 -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='stock_db'"
if ($dbExists.Trim() -ne "1") {
    Write-Host "Creating stock_db and restoring stock.backup..." -ForegroundColor Yellow
    & $createdb -h 127.0.0.1 -p 5433 -U postgres stock_db
    if ($LASTEXITCODE -ne 0) {
        throw "createdb failed with exit code $LASTEXITCODE."
    }

    if (-not (Test-Path $backupFile)) {
        throw "Backup file not found at $backupFile."
    }

    & $pgRestore -h 127.0.0.1 -p 5433 -U postgres -d stock_db --no-owner --no-privileges $backupFile
    if ($LASTEXITCODE -ne 0) {
        throw "pg_restore failed with exit code $LASTEXITCODE."
    }

    Push-Location $scriptPath
    try {
        alembic upgrade head
        if ($LASTEXITCODE -ne 0) {
            throw "alembic upgrade head failed with exit code $LASTEXITCODE."
        }
    }
    finally {
        Pop-Location
    }
}

Write-Host "Local PostgreSQL is ready at 127.0.0.1:5433/stock_db" -ForegroundColor Green
