<#!
.SYNOPSIS
  One-click launcher for MauEyeCare on Windows.
.DESCRIPTION
  Starts the backend API (Uvicorn) and optionally the frontend (Vite) if a package.json is present.
  Performs a health check for the backend and opens the browser to the frontend URL if available.
  Gracefully stops background jobs on exit.
#>
# Parameter handling removed to avoid host-injected binding errors.
# Defaults can be edited here if needed.
$Frontend = 'dev'
$ApiPort = 8000
$WebPort = 5173

$ErrorActionPreference = 'Stop'
Write-Host "[MauEyeCare] Launching..." -ForegroundColor Cyan

# Ensure venv exists
$pythonPath = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (!(Test-Path $pythonPath)) {
  Write-Error ".venv not found or incomplete. Run setup.ps1 first."; exit 1
}

# Start backend in background
$apiUrl = "http://127.0.0.1:$ApiPort"
$healthUrl = "$apiUrl/api/health"

Write-Host "Starting backend API on $apiUrl ..." -ForegroundColor Yellow
try {
  $backendProc = Start-Process -FilePath "powershell" -ArgumentList @(
    "-NoProfile","-ExecutionPolicy","Bypass","-Command",
    "& `"$pythonPath`" -m uvicorn main:app --host 127.0.0.1 --port $ApiPort"
  ) -PassThru -WorkingDirectory $PSScriptRoot
} catch {
  Write-Error "Failed to start backend: $($_.Exception.Message)"; exit 1
}

# Wait for backend health
$healthy = $false
for ($i = 1; $i -le 30; $i++) {
  try {
    $resp = Invoke-RestMethod -Uri $healthUrl -Method Get -TimeoutSec 2
    if ($resp.status -eq 'ok') { $healthy = $true; break }
  } catch {}
  Start-Sleep -Milliseconds 500
}
if (-not $healthy) {
  Write-Warning "Backend health check failed at $healthUrl. Terminating process."
  try { if ($backendProc) { Stop-Process -Id $backendProc.Id -Force } } catch {}
  Write-Error "Backend did not become healthy. Exiting."; exit 1
}
Write-Host "Backend is healthy at $apiUrl" -ForegroundColor Green

# Optionally start frontend
$frontendStarted = $false
$hasPkg = [System.IO.File]::Exists((Join-Path $PSScriptRoot 'package.json'))
$hasNpm = $false
try { & where.exe npm *> $null; if ($LASTEXITCODE -eq 0) { $hasNpm = $true } } catch {}
if ($hasPkg -and $Frontend -ne 'none' -and $hasNpm) {
  switch ($Frontend) {
    'dev' {
      Write-Host "Starting frontend (npm run dev) on http://localhost:$WebPort ..." -ForegroundColor Yellow
      try {
        $frontendProc = Start-Process -FilePath "npm" -ArgumentList @("run","dev","--","--host","127.0.0.1","--port","$WebPort") -PassThru
        $frontendStarted = $true
      } catch {
        Write-Warning "Failed to start frontend dev server: $($_.Exception.Message)"
      }
    }
    'preview' {
      Write-Host "Building and starting frontend preview..." -ForegroundColor Yellow
      try {
        Start-Process -FilePath "npm" -ArgumentList @("run","build") -Wait
        $frontendProc = Start-Process -FilePath "npm" -ArgumentList @("run","preview") -PassThru
        $frontendStarted = $true
      } catch {
        Write-Warning "Failed to build/preview frontend: $($_.Exception.Message)"
      }
    }
  }
}

# Optionally open browser
if ($frontendStarted) {
  Start-Sleep -Seconds 2
  $webUrl = "http://localhost:$WebPort"
  Write-Host "Opening $webUrl ..." -ForegroundColor Cyan
  try { Start-Process $webUrl } catch {}
} else {
  # Open API docs as a friendly landing page if no frontend
  $docsUrl = "$apiUrl/docs"
  Write-Host "Opening API docs at $docsUrl ..." -ForegroundColor Cyan
  try { Start-Process $docsUrl } catch {}
}

Write-Host "MauEyeCare is running in separate windows. You can close this launcher." -ForegroundColor DarkGray