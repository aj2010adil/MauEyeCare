<#
.SYNOPSIS
    One‑click launcher for MauEyeCare on Windows 11
.DESCRIPTION
    - Checks dependencies & ports
    - Auto‑detects frontend location
    - Starts backend (FastAPI) + frontend (Vite/React)
    - Opens browser automatically
#>

Write-Host "`n=== MauEyeCare One‑Click Launcher ===" -ForegroundColor Cyan

# -----------------------------
# CONFIG
# -----------------------------
$backendFolder = "backend"   # Change if backend lives elsewhere
$frontendCandidates = @("frontend", "ui", ".")
$backendPort = 8000
$frontendPort = 5173
$dbServiceName = "postgresql-x64-15"  # Change if your PG version differs

# -----------------------------
# FUNCTIONS
# -----------------------------
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

# -----------------------------
# PRECHECKS
# -----------------------------
if (-not (Get-Command npm.cmd -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Node.js not found — install from https://nodejs.org" -ForegroundColor Red
    exit 1
}
if (-not (Get-Command uvicorn.exe -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: uvicorn not found — run 'pip install uvicorn[standard]'" -ForegroundColor Red
    exit 1
}
if (-not (Test-PortFree $backendPort)) {
    Write-Host "ERROR: Port $backendPort in use — close the process and try again." -ForegroundColor Red
    exit 1
}
if (-not (Test-PortFree $frontendPort)) {
    Write-Host "ERROR: Port $frontendPort in use — close the process and try again." -ForegroundColor Red
    exit 1
}

# -----------------------------
# FRONTEND PATH DETECTION
# -----------------------------
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

# -----------------------------
# DB CHECK
# -----------------------------
if (-not (Start-IfStopped $dbServiceName)) {
    Write-Host "WARNING: PostgreSQL service '$dbServiceName' not found or not running." -ForegroundColor Yellow
}

# -----------------------------
# START BACKEND
# -----------------------------
if (-not (Test-Path $backendFolder)) {
    Write-Host "ERROR: Backend folder '$backendFolder' not found." -ForegroundColor Red
    exit 1
}
Write-Host "`n[1/3] Starting backend..." -ForegroundColor Green
Start-Process "uvicorn.exe" -ArgumentList "$($backendFolder.Replace('\','/')).app.main:app", "--reload", "--port", "$backendPort" -WorkingDirectory (Resolve-Path $backendFolder)

# -----------------------------
# START FRONTEND
# -----------------------------
Write-Host "`n[2/3] Starting frontend..." -ForegroundColor Green
Push-Location $frontendPath
& npm.cmd install
Start-Process "npm.cmd" -ArgumentList "run", "dev" -WorkingDirectory $frontendPath
Pop-Location

# -----------------------------
# OPEN APP IN BROWSER
# -----------------------------
Write-Host "`n[3/3] Launching browser..." -ForegroundColor Green
Start-Sleep -Seconds 3
Start-Process "http://localhost:$frontendPort/"

Write-Host "`nMauEyeCare is starting — backend on :$backendPort, frontend on :$frontendPort" -ForegroundColor Cyan
Write-Host "Keep this window open; close it to stop servers.`n" -ForegroundColor Yellow
