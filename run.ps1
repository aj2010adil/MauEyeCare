<#!
.SYNOPSIS
  One-click launcher for MauEyeCare on Windows.
.DESCRIPTION
  Starts the backend API (Uvicorn) and optionally the frontend (Vite) if a package.json is present.
  Performs a health check for the backend and opens the browser to the frontend URL if available.
  Gracefully stops background jobs on exit.
#>
[CmdletBinding()]
param(
  [ValidateSet('dev','preview','none')]
  [string]$Frontend = 'dev',
  [int]$ApiPort = 8000,
  [int]$WebPort = 5173
)

$ErrorActionPreference = 'Stop'
Write-Host "[MauEyeCare] Launching..." -ForegroundColor Cyan

# Ensure venv exists
if (!(Test-Path .\.venv\Scripts\python.exe)) {
  Write-Error ".venv not found or incomplete. Run setup.ps1 first."; exit 1
}

# Start backend in background
$apiUrl = "http://127.0.0.1:$ApiPort"
$healthUrl = "$apiUrl/api/health"

Write-Host "Starting backend API on $apiUrl ..." -ForegroundColor Yellow
try {
  $backendJob = Start-Job -Name "mau-backend" -ScriptBlock {
    & .\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port $using:ApiPort
  }
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
  Write-Warning "Backend health check failed at $healthUrl. Logs follow:"
  Receive-Job -Id $backendJob.Id -Keep | Write-Host
  Write-Error "Backend did not become healthy. Exiting."; Get-Job -Id $backendJob.Id | Stop-Job -Force | Out-Null; Remove-Job -Id $backendJob.Id -Force; exit 1
}
Write-Host "Backend is healthy at $apiUrl" -ForegroundColor Green

# Optionally start frontend
$frontendStarted = $false
if (Test-Path package.json -and $Frontend -ne 'none') {
  switch ($Frontend) {
    'dev' {
      Write-Host "Starting frontend (npm run dev) on http://localhost:$WebPort ..." -ForegroundColor Yellow
      try {
        $frontendJob = Start-Job -Name "mau-frontend" -ScriptBlock {
          if (!(Get-Command npm -ErrorAction SilentlyContinue)) { throw "npm not found" }
          npm run dev
        }
        $frontendStarted = $true
      } catch {
        Write-Warning "Failed to start frontend dev server: $($_.Exception.Message)"
      }
    }
    'preview' {
      Write-Host "Building and starting frontend preview..." -ForegroundColor Yellow
      try {
        if (!(Get-Command npm -ErrorAction SilentlyContinue)) { throw "npm not found" }
        npm run build
        $frontendJob = Start-Job -Name "mau-frontend" -ScriptBlock {
          npm run preview
        }
        $frontendStarted = $true
      } catch {
        Write-Warning "Failed to build/preview frontend: $($_.Exception.Message)"
      }
    }
  }
}

# Optionally open browser
if ($frontendStarted) {
  # Wait a bit for the dev server to boot
  Start-Sleep -Seconds 2
  $webUrl = "http://localhost:$WebPort"
  Write-Host "Opening $webUrl ..." -ForegroundColor Cyan
  try { Start-Process $webUrl } catch {}
} else {
  Write-Host "Frontend not started (no package.json or Frontend='$Frontend'). API available at $apiUrl" -ForegroundColor DarkYellow
}

Write-Host "Press Ctrl+C to stop. Logs are streaming below (backend)." -ForegroundColor DarkGray

# Stream backend logs; on Ctrl+C, clean up
try {
  while ($true) {
    Receive-Job -Name "mau-backend" -Keep | ForEach-Object { $_ }
    Start-Sleep -Milliseconds 500
  }
} finally {
  Write-Host "Shutting down..." -ForegroundColor Yellow
  if ($frontendStarted) { Get-Job -Name "mau-frontend" -ErrorAction SilentlyContinue | Stop-Job -Force | Remove-Job -Force | Out-Null }
  Get-Job -Name "mau-backend" -ErrorAction SilentlyContinue | Stop-Job -Force | Remove-Job -Force | Out-Null
  Write-Host "Cleanup complete."
}