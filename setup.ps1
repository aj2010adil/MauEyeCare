<#
.SYNOPSIS
    Environment setup for MauEyeCare on Windows 11
.DESCRIPTION
    Installs backend/frontend dependencies, runs DB migrations, and seeds initial data.
#>

Write-Host "`n=== MauEyeCare Setup Script ===" -ForegroundColor Cyan

# --- CONFIG ---
$pythonExe = "python"
$backendFolder = "."
$frontendCandidates = @("frontend", "ui", ".")
$seedFile = "seed.sql"
$dbServiceName = "postgresql-x64-15"

# --- FUNCTIONS ---
function Ensure-Command($cmd, $installMsg) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: $cmd not found. $installMsg" -ForegroundColor Red
        exit 1
    }
}

# --- PRECHECKS ---
Ensure-Command $pythonExe "Install Python 3.11+ from https://www.python.org"
Ensure-Command "npm.cmd" "Install Node.js from https://nodejs.org"
Ensure-Command "psql" "Install PostgreSQL and ensure psql is in PATH"

# --- START DB SERVICE ---
$svc = Get-Service -Name $dbServiceName -ErrorAction SilentlyContinue
if ($null -ne $svc -and $svc.Status -ne 'Running') {
    Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
    Start-Service $dbServiceName
}

# --- BACKEND SETUP ---
Write-Host "`n[1/4] Installing backend dependencies..." -ForegroundColor Green
Push-Location $backendFolder
& $pythonExe -m pip install --upgrade pip
& $pythonExe -m pip install -r requirements.txt
Pop-Location

# --- FRONTEND SETUP ---
Write-Host "`n[2/4] Installing frontend dependencies..." -ForegroundColor Green
$frontendPath = $null
foreach ($candidate in $frontendCandidates) {
    if (Test-Path (Join-Path $candidate "package.json")) {
        $frontendPath = Resolve-Path $candidate
        break
    }
}
if (-not $frontendPath) {
    Write-Host "ERROR: Could not find frontend folder with package.json" -ForegroundColor Red
    exit 1
}
Push-Location $frontendPath
& npm.cmd install
Pop-Location

# --- DB MIGRATIONS ---
Write-Host "`n[3/4] Running Alembic migrations..." -ForegroundColor Green
Push-Location $backendFolder
& $pythonExe -m alembic upgrade head
Pop-Location

# --- DB SEED ---
if (Test-Path $seedFile) {
    Write-Host "`n[4/4] Seeding database from $seedFile..." -ForegroundColor Green
    & psql -U postgres -d mau_eyecare -f $seedFile
} else {
    Write-Host "WARNING: Seed file $seedFile not found. Skipping seed step." -ForegroundColor Yellow
}

Write-Host "`nSetup complete! You can now run .\run.ps1 to start MauEyeCare." -ForegroundColor Cyan
