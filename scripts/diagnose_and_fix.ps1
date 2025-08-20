param(
  [string]$ApiHost = '127.0.0.1',
  [int]$ApiPort = 8001,
  [string]$Email = 'doctor@maueyecare.com',
  [string]$Password = 'changeme'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "[Diagnose] Starting checks..." -ForegroundColor Cyan

# 1) Ensure venv deps installed (python-multipart etc.)
& .\.venv\Scripts\pip install --disable-pip-version-check -q -r requirements.txt | Out-Null

# 2) Apply migrations
& .\.venv\Scripts\python -m alembic upgrade head

# 3) Seed/reset default user to requested password
$env:MAU_ADMIN_EMAIL = $Email
$env:MAU_ADMIN_PASSWORD = $Password
& .\.venv\Scripts\python .\reset_admin.py

# 4) Free backend port
try { Get-NetTCPConnection -LocalPort $ApiPort -ErrorAction SilentlyContinue | Select OwningProcess -Unique | % { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue } } catch {}

# 5) Start backend and wait for health
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = (Resolve-Path .\.venv\Scripts\python.exe).Path
$psi.Arguments = "-m uvicorn main:app --host $ApiHost --port $ApiPort --log-level info"
$psi.WorkingDirectory = (Get-Location).Path
$psi.RedirectStandardOutput = $true
$psi.RedirectStandardError = $true
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$proc = New-Object System.Diagnostics.Process
$proc.StartInfo = $psi
$null = $proc.Start()
Start-Sleep -Seconds 2

$healthy = $false
for ($i=1; $i -le 20; $i++) {
  try {
    $h = Invoke-RestMethod -Method GET -Uri "http://${ApiHost}:${ApiPort}/api/health" -TimeoutSec 2
    if ($h.status -eq 'ok') { $healthy = $true; break }
  } catch {}
  Start-Sleep -Seconds 1
}
if (-not $healthy) {
  Write-Host "[Diagnose] Backend not healthy on ${ApiHost}:${ApiPort}. Recent output:" -ForegroundColor Yellow
  try { $out = $proc.StandardError.ReadToEnd(); if ($out) { Write-Host $out } } catch {}
  try { $out2 = $proc.StandardOutput.ReadToEnd(); if ($out2) { Write-Host $out2 } } catch {}
  throw "Backend failed to become healthy"
}
Write-Host "[Diagnose] Backend healthy at http://${ApiHost}:${ApiPort}/api/health" -ForegroundColor Green

# 6) Test login with requested credentials
$form = @{ username = $Email; password = $Password; grant_type='password' }
$token = Invoke-RestMethod -Method POST -Uri "http://${ApiHost}:${ApiPort}/api/auth/login" -ContentType 'application/x-www-form-urlencoded' -Body $form
if (-not $token.access_token) { throw "Login did not return access_token" }
Write-Host "[Diagnose] Login OK for $Email" -ForegroundColor Green

try { if ($proc -and !$proc.HasExited) { $proc.Kill() } } catch {}
Write-Host "[Diagnose] All checks passed. You can now login at http://localhost:5173/login with $Email / $Password" -ForegroundColor Cyan


