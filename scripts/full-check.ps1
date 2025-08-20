param(
  [string]$ApiHost = '127.0.0.1',
  [int]$ApiPort = 8001,
  [string]$Email = $env:MAU_ADMIN_EMAIL,
  [string]$Password = $env:MAU_ADMIN_PASSWORD
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $Email) { $Email = 'doctor@maueyecare.com' }
if (-not $Password) { $Password = 'MauEyeCareAdmin@2024' }

# Create logs folder and start transcript
$logDir = Join-Path $PSScriptRoot '..' | Resolve-Path | ForEach-Object { Join-Path $_ 'logs' }
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$logFile = Join-Path $logDir "full-check-$ts.log"
Start-Transcript -Path $logFile -Append | Out-Null

Write-Host "[Full-Check] Starting end-to-end verification..." -ForegroundColor Cyan

$results = [ordered]@{
  DbMigrations = $false
  ResetAdmin    = $false
  DbConnectivity= $false
  BackendReady  = $false
  ApiLogin      = $false
}

function Invoke-Step($Name, [ScriptBlock]$Action) {
  Write-Host "[Step] $Name" -ForegroundColor Yellow
  try {
    & $Action
    Write-Host "[ OK ] $Name" -ForegroundColor Green
    return $true
  } catch {
    Write-Host "[FAIL] $Name -> $($_.Exception.Message)" -ForegroundColor Red
    return $false
  }
}

# 1) Apply Alembic migrations
$results.DbMigrations = Invoke-Step 'Apply migrations (alembic upgrade head)' {
  & .\.venv\Scripts\python -m alembic upgrade head
  if ($LASTEXITCODE -ne 0) { throw "alembic returned non-zero exit code $LASTEXITCODE" }
}

# 2) Ensure default admin user exists and password is correct
$results.ResetAdmin = Invoke-Step 'Reset/Create default admin user' {
  & .\.venv\Scripts\python .\reset_admin.py
  if ($LASTEXITCODE -ne 0) { throw "reset_admin.py returned non-zero exit code $LASTEXITCODE" }
}

# 3) DB connectivity + users table presence
$results.DbConnectivity = Invoke-Step 'DB connectivity and users table check' {
  & .\scripts\db-test.ps1
  if ($LASTEXITCODE -ne 0) { throw "db-test.ps1 returned non-zero exit code $LASTEXITCODE" }
}

# 4) Start backend on given port and wait for health
$backendJob = $null
$results.BackendReady = Invoke-Step "Start backend on ${ApiHost}:${ApiPort} and wait for health" {
  if (Get-Job -Name fullcheck-backend -ErrorAction SilentlyContinue) {
    Get-Job -Name fullcheck-backend | Stop-Job -Force | Remove-Job -Force
  }
  $backendJob = Start-Job -Name fullcheck-backend -ScriptBlock { & .\.venv\Scripts\uvicorn main:app --host 127.0.0.1 --port $using:ApiPort --log-level debug }
  Start-Sleep -Seconds 2

  $healthOk = $false
  for ($i=1; $i -le 30; $i++) {
    try {
      $h = Invoke-RestMethod -Method GET -Uri "http://${ApiHost}:${ApiPort}/api/health" -TimeoutSec 2
      if ($h.status -eq 'ok') { $healthOk = $true; break }
    } catch {
      Write-Host "[Health] Attempt $i failed: $($_.Exception.Message)" -ForegroundColor DarkGray
    }
    Start-Sleep -Seconds 1
  }
  if (-not $healthOk) {
    Write-Host "[Backend] Recent logs:" -ForegroundColor Yellow
    Receive-Job -Id $backendJob.Id -Keep -ErrorAction SilentlyContinue | Select-Object -Last 200 | Write-Output
    throw "Backend did not become healthy on port $ApiPort"
  }
}

# 5) API smoke: login and refresh
$results.ApiLogin = Invoke-Step 'API smoke test (login + refresh)' {
  & .\scripts\api-smoke.ps1 -ApiBase "http://${ApiHost}:${ApiPort}" -Email $Email -Password $Password
  if ($LASTEXITCODE -ne 0) { throw "api-smoke.ps1 returned non-zero exit code $LASTEXITCODE" }
}

# Stop backend job
if ($backendJob) {
  Get-Job -Id $backendJob.Id | Stop-Job -Force -ErrorAction SilentlyContinue | Out-Null
  Get-Job -Id $backendJob.Id | Remove-Job -Force -ErrorAction SilentlyContinue | Out-Null
}

Write-Host "`n=== Summary ===" -ForegroundColor Cyan
$failCount = 0
foreach ($k in $results.Keys) {
  $v = $results[$k]
  if ($v) { Write-Host ("{0,-16} : PASS" -f $k) -ForegroundColor Green }
  else { Write-Host ("{0,-16} : FAIL" -f $k) -ForegroundColor Red; $failCount++ }
}
Write-Host "Log file: $logFile" -ForegroundColor Yellow

Stop-Transcript | Out-Null

if ($failCount -gt 0) { exit 1 } else { exit 0 }


