<#
.SYNOPSIS
    One-click launcher for MauEyeCare
.DESCRIPTION
    Cleans caches, starts backend (FastAPI) + frontend (Vite/React), and opens browser.
#>

Write-Host "`n=== MauEyeCare One‑Click Launcher ===" -ForegroundColor Cyan

# --- CONFIG ---
$backendFolder   = "backend"
$frontendFolder  = "MauEyeCareLauncher"
$backendPort     = 8000
$frontendPort    = 5173
$dbServiceName   = "postgresql-x64-15"

# --- FUNCTIONS ---
function Test-PortFree {
    param([int]$Port)
    $inUse = netstat -ano | Select-String ":$Port " | ForEach-Object { $_.ToString().Trim() }
    return -not $inUse
}
function Start-IfStopped {
    param([string]$ServiceName)
    $svc = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($null -eq $svc) { return $false }
    if ($svc.Status -ne 'Running') {
        Write-Host "Starting service: $ServiceName" -ForegroundColor Yellow
        Start-Service $ServiceName
    }
    return $true
}

# --- CLEAN CACHES ---
if (Test-Path ".pytest_cache") {
    Remove-Item -Recurse -Force ".pytest_cache"
    Write-Host "Removed .pytest_cache" -ForegroundColor Yellow
}

# --- PRECHECKS ---
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js not found" -ForegroundColor Red
    exit 1
}
if (-not (Get-Command uvicorn.exe -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: uvicorn not found" -ForegroundColor Red
    exit 1
}
if (-not (Test-PortFree $backendPort)) {
    Write-Host "ERROR: Port $backendPort in use" -ForegroundColor Red
    exit 1
}
if (-not (Test-PortFree $frontendPort)) {
    Write-Host "ERROR: Port $frontendPort in use" -ForegroundColor Red
    exit 1
}

# --- START DB SERVICE ---
if (-not (Start-IfStopped $dbServiceName)) {
    Write-Host "WARNING: PostgreSQL '$dbServiceName' not running." -ForegroundColor Yellow
}

# --- BACKEND TARGET DETECTION ---
if (Test-Path (Join-Path $backendFolder "app\main.py")) {
    $uvicornTarget = "app.main:app"
} elseif (Test-Path (Join-Path $backendFolder "main.py")) {
    $uvicornTarget = "main:app"
} else {
    Write-Host "ERROR: Could not find FastAPI entrypoint in $backendFolder" -ForegroundColor Red
    exit 1
}

# --- START BACKEND ---
Write-Host "`n[1/3] Starting backend..." -ForegroundColor Green
Start-Process "uvicorn.exe" -ArgumentList $uvicornTarget, "--reload", "--port", "$backendPort" -WorkingDirectory (Resolve-Path $backendFolder)

# --- START FRONTEND ---
$frontendPath = Resolve-Path $frontendFolder
if (-not (Test-Path (Join-Path $frontendPath "package.json"))) {
    Write-Host "ERROR: package.json not found in $frontendFolder" -ForegroundColor Red
    exit 1
}
Write-Host "`n[2/3] Starting frontend..." -ForegroundColor Green
Push-Location $frontendPath
& npm.cmd install
Start-Process "npm.cmd" -ArgumentList "run", "dev" -WorkingDirectory $frontendPath
Pop-Location

# --- OPEN APP ---
Write-Host "`n[3/3] Launching browser..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://localhost:$frontendPort/"

Write-Host "`nMauEyeCare is running — backend :$backendPort, frontend :$frontendPort" -ForegroundColor Cyan
Write-Host "Keep this window open; close to stop servers.`n" -ForegroundColor Yellow
