param([switch]$FixCommon)
Write-Host "[MauEyeCare] Diagnostics" -ForegroundColor Cyan

function Test-Port($port){
  try { $l = New-Object System.Net.Sockets.TcpClient('127.0.0.1', $port); $l.Close(); return $true } catch { return $false }
}

Write-Host "Python: $(py -3 --version 2>$null)" -ForegroundColor Yellow
Write-Host "Node: $(node -v 2>$null)" -ForegroundColor Yellow

if (!(Test-Path .venv)) { Write-Warning ".venv missing" }
if ($FixCommon -and !(Test-Path .venv)) { py -3 -m venv .venv }

if ($FixCommon) {
  if (Test-Path requirements.txt) { & .\.venv\Scripts\pip install -r requirements.txt }
  if (Test-Path package.json) { npm install }
}

Write-Host "Port 8000 open: $(Test-Port 8000)" -ForegroundColor Yellow
Write-Host "Port 5173 open: $(Test-Port 5173)" -ForegroundColor Yellow

Write-Host "Done." -ForegroundColor Green

