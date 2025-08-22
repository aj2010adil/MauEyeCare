<#
.SYNOPSIS
    One‑click launcher for MauEyeCare on Windows 11
.DESCRIPTION
    - Checks dependencies & ports
    - Cleans problematic cache dirs
    - Auto‑detects backend & frontend locations
    - Starts backend (FastAPI) + frontend (Vite/React)
    - Opens browser automatically
#>

Write-Host "`n=== MauEyeCare One‑Click Launcher ===" -ForegroundColor Cyan

# -----------------------------
# CONFIG
# -----------------------------
$backendFolderCandidates = @(".", "backend", "server", "api")
$frontendCandidates = @("frontend", "ui", ".")
$backendPort = 8000
$frontendPort = 5173
$dbServiceName = "postgresql-x64-15"  # Adjust for your Postgres version

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
