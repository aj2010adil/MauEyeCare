<#
.SYNOPSIS
    Environment setup for MauEyeCare (Windows 11)
.DESCRIPTION
    Installs backend & frontend dependencies, runs Alembic migrations, and seeds initial data.
#>

Write-Host "`n=== MauEyeCare Setup Script ===" -ForegroundColor Cyan

# --- CONFIG ---
$pythonExe      = "python"
$dbServiceName  = "postgresql-x64-15"
$backendFolder  = "backend"
$frontendFolder = "frontend"

# --- FUNCTIONS ---
function Ensure-Command($cmd, $installMsg) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: $cmd not found. $installMsg" -ForegroundColor Red
        exit 1
    }
}

# --- PRECHECKS ---
Ensure-Command $pythonExe "Install Python 3.11+ from https://www.python.org"
Ensure-Command "npm.cmd"   "Install Node.js from https://nodejs.org"
Ensure-Command "psql"      "Install PostgreSQL and ensure psql is in PATH"

# --- START DB SERVICE ---
$svc = Get-Service -Name $dbServiceName -ErrorAction SilentlyContinue
if ($null -ne $svc -and $svc.Status -ne 'Running') {
    Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
    Start-Service $dbServiceName
}

# --- BACKEND SETUP ---
$reqFile = Join-Path $backendFolder "requirements.txt"
if (-not (Test-Path $reqFile)) {
    Write-Host "ERROR: Backend requirements.txt not found in $backendFolder" -ForegroundColor Red
    exit 1
}
Write-Host "`n[1/4] Installing backend dependencies..." -ForegroundColor Green
Push-Location $backendFolder
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r requirements.txt
Pop-Location

# --- FRONTEND SETUP ---
$pkgFile = Join-Path $frontendFolder "package.json"
if (-not (Test-Path $pkgFile)) {
    Write-Host "ERROR: Frontend package.json not found in $frontendFolder" -ForegroundColor Red
    exit 1
}
Write-Host "`n[2/4] Installing frontend dependencies..." -ForegroundColor Green
Push-Location $frontendFolder
& npm.cmd install
Pop-Location

# --- DB MIGRATIONS ---
$alembicFile = Join-Path $backendFolder "alembic.ini"
if (-not (Test-Path $alembicFile)) {
    Write-Host "ERROR: alembic.ini not found in $backendFolder" -ForegroundColor Red
    exit 1
}
Write-Host "`n[3/4] Running Alembic migrations..." -ForegroundColor Green
Push-Location $backendFolder
& $pythonExe -m alembic -c alembic.ini upgrade head
Pop-Location

# --- DB SEED ---
$seedFile = Join-Path $backendFolder "seed.sql"
if (Test-Path $seedFile) {
    Write-Host "`n[4/4] Seeding database from $seedFile..." -ForegroundColor Green
    & psql -U postgres -d mau_eyecare -f $seedFile
}
else {
    Write-Host "WARNING: Seed file not found in $backendFolder. Skipping seed step." -ForegroundColor Yellow
}

Write-Host "`nSetup complete! You can now run .\run.ps1 to start MauEyeCare." -ForegroundColor Cyan
