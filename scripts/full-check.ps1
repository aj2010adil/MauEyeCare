param(
  [string]$ApiHost = '127.0.0.1',
  [int]$ApiPort = 8000,
  [string]$Email = $env:MAU_ADMIN_EMAIL,
  [string]$Password = $env:MAU_ADMIN_PASSWORD
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if (-not $Email) { $Email = 'doctor@maueyecare.com' }
if (-not $Password) { $Password = 'MauEyeCareAdmin@2024' }

# Create logs folder and start transcript
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$logDir = Join-Path $repoRoot 'logs'
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
# 0) Ensure port is free
Invoke-Step "Free port ${ApiPort} if occupied" {
  try {
    $conns = Get-NetTCPConnection -LocalPort $ApiPort -ErrorAction SilentlyContinue
    if ($conns) {
      $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
      foreach ($pid in $pids) {
        try { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue } catch {}
      }
      Start-Sleep -Seconds 1
    }
    $still = Get-NetTCPConnection -LocalPort $ApiPort -ErrorAction SilentlyContinue
    if ($still) { throw "Port $ApiPort still in use by PID(s): $($still | Select-Object -ExpandProperty OwningProcess -Unique -Join ',')" }
  } catch {}
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
${null} = New-Item -ItemType Directory -Force -Path $logDir
$backendLog = Join-Path $logDir "backend-$ts.log"
$backendProc = $null
$results.BackendReady = Invoke-Step "Start backend on ${ApiHost}:${ApiPort} and wait for health" {
  try {
    if ($backendProc -and !$backendProc.HasExited) { $backendProc.Kill() }
  } catch {}
  # Start backend as a process with stdout/stderr redirected to a log file
  $psi = New-Object System.Diagnostics.ProcessStartInfo
  $psi.FileName = (Resolve-Path .\.venv\Scripts\python.exe).Path
  $psi.Arguments = "-m uvicorn main:app --host 127.0.0.1 --port $ApiPort --log-level debug"
  $psi.WorkingDirectory = $repoRoot
  $psi.RedirectStandardOutput = $true
  $psi.RedirectStandardError = $true
  $psi.UseShellExecute = $false
  $psi.CreateNoWindow = $true
  $backendProc = New-Object System.Diagnostics.Process
  $backendProc.StartInfo = $psi
  $null = $backendProc.Start()
  # Async write of output to file
  $stdOut = $backendProc.StandardOutput
  $stdErr = $backendProc.StandardError
  Start-Job -Name fullcheck-backendlog -ScriptBlock {
    param($outReader, $errReader, $logPath)
    try {
      $sw = New-Object System.IO.StreamWriter($logPath, $true)
      while ($true) {
        if ($outReader.EndOfStream -and $errReader.EndOfStream) { Start-Sleep -Milliseconds 200 }
        while (-not $outReader.EndOfStream) { $sw.WriteLine($outReader.ReadLine()) }
        while (-not $errReader.EndOfStream) { $sw.WriteLine($errReader.ReadLine()) }
        $sw.Flush()
        Start-Sleep -Milliseconds 200
      }
    } catch {}
  } -ArgumentList $stdOut, $stdErr, $backendLog | Out-Null
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
    if (Test-Path $backendLog) { Get-Content -Path $backendLog -Tail 200 }
    Write-Host "[Backend] Netstat:" -ForegroundColor Yellow
    netstat -ano | Select-String ":${ApiPort}\s" | Write-Output
    throw "Backend did not become healthy on port $ApiPort"
  }
}

# 5) API smoke: login and refresh
$results.ApiLogin = Invoke-Step 'API smoke test (login + refresh)' {
  & .\scripts\api-smoke.ps1 -ApiBase "http://${ApiHost}:${ApiPort}" -Email $Email -Password $Password
  if ($LASTEXITCODE -ne 0) { throw "api-smoke.ps1 returned non-zero exit code $LASTEXITCODE" }
}

# Stop backend job
try { if ($backendProc -and !$backendProc.HasExited) { $backendProc.Kill() } } catch {}
if (Get-Job -Name fullcheck-backendlog -ErrorAction SilentlyContinue) {
  try { Get-Job -Name fullcheck-backendlog | Stop-Job -ErrorAction SilentlyContinue } catch {}
  try { Get-Job -Name fullcheck-backendlog | Remove-Job -ErrorAction SilentlyContinue } catch {}
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


