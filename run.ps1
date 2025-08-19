Write-Host "[MauEyeCare] Starting backend and frontend..." -ForegroundColor Cyan
$ErrorActionPreference = 'Stop'

if (!(Test-Path .venv)) { Write-Error ".venv not found. Run scripts/setup.ps1 first."; exit 1 }

function Get-LocalIPv4 {
  $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-*","Ethernet*" -ErrorAction SilentlyContinue | Where-Object {$_.IPAddress -notmatch "^169\.254\."} | Select-Object -First 1).IPAddress
  if (!$ip) { $ip = '127.0.0.1' }
  return $ip
}

$ip = Get-LocalIPv4
Write-Host "LAN IP: http://$ip:5173" -ForegroundColor Yellow

Start-Job -Name "backend" -ScriptBlock { & .\.venv\Scripts\uvicorn main:app --host 0.0.0.0 --port 8000 } | Out-Null
Start-Sleep -Seconds 2
npm run dev

Get-Job | Stop-Job | Remove-Job

