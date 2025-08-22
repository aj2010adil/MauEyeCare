<#
.SYNOPSIS
    Environment setup for MauEyeCare (Windows 11)
.DESCRIPTION
    Installs backend & frontend dependencies, runs Alembic migrations, and seeds initial data.
#>

Write-Host "`n=== MauEyeCare Setup Script ===" -ForegroundColor Cyan

# --- FUNCTIONS ---
function Ensure-Command($cmd, $installMsg) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: $cmd not found. $installMsg" -ForegroundColor Red
        exit 1
    }
}

# --- PRECHECKS ---
Ensure-Command "python"   "Install Python 3.11+ from https://www.python.org"
Ensure-Command "npm.cmd"  "Install Node.js from https://nodejs.org"
Ensure-Command "psql"     "Install PostgreSQL and ensure psql is in PATH"

# --- START DB SERVICE ---
$dbServiceName = "postgresql-x64-15"
$svc = Get-Service -Name $dbServiceName -ErrorAction SilentlyContinue
if ($null -ne $svc -and $svc.Status -ne 'Running') {
    Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
    Start-Service $dbServiceName
}

# --- LOCATE BACKEND ---
$backendPath = Get-ChildItem -Directory -Recurse -Depth 2 |
    Where-Object { 
        Test-Path (Join-Path $_.FullName "requirements.txt") -and 
        Test-Path (Join-Path $_.FullName "alembic.ini")
    } | Select-Object -First 1 -ExpandProperty FullName

if (-not $backendPath) {
    Write-Host "ERROR: Could not locate backend folder with requirements.txt & alembic.ini" -ForegroundColor Red
    exit 1
}

# --- BACKEND SETUP ---
Write-Host "`n[1/4] Installing backend dependencies from $backendPath..." -ForegroundColor Green
Push-Location $backendPath
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Pop-Location

# --- LOCATE FRONTEND ---
$frontendPath = Get-ChildItem -Directory -Recurse -Depth 2 |
    Where-Object { 
        Test-Path (Join-Path $_.FullName "package.json") -and 
        $_.FullName -notmatch "node_modules"
    } | Select-Object -First 1 -ExpandProperty FullName

if (-not $frontendPath) {
    Write-Host "ERROR: Could not locate frontend folder with package.json" -ForegroundColor Red
    exit 1
}

# --- FRONTEND SETUP ---
Write-Host "`n[2/4] Installing frontend dependencies from $frontendPath..." -ForegroundColor Green
Push-Location $frontendPath
npm.cmd install
Pop-Location

# --- DB MIGRATIONS ---
Write-Host "`n[3/4] Running Alembic migrations..." -ForegroundColor Green
Push-Location $backendPath
python