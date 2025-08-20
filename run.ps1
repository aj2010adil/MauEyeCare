param(
  [string]$BindHost = '0.0.0.0',
  [int]$BindPort = 8000
)

Write-Host "[MauEyeCare] Starting backend (${BindHost}:${BindPort}) and frontend..." -ForegroundColor Cyan
$ErrorActionPreference = 'Stop'

if (!(Test-Path .venv)) { Write-Error ".venv not found. Run scripts/setup.ps1 first."; exit 1 }

function Get-LocalIPv4 {
  $ip = (Get-NetIPAddress -AddressFamily IPv4 -InterfaceAlias "Wi-*","Ethernet*" -ErrorAction SilentlyContinue | Where-Object {$_.IPAddress -notmatch "^169\.254\."} | Select-Object -First 1).IPAddress
  if (!$ip) { $ip = '127.0.0.1' }
  return $ip
}

$ip = Get-LocalIPv4
Write-Host "LAN IP (frontend): http://$ip:5173" -ForegroundColor Yellow
Write-Host "Backend health: http://127.0.0.1:${BindPort}/api/health" -ForegroundColor Yellow

if (Get-Job -Name backend -ErrorAction SilentlyContinue) { Get-Job -Name backend | Stop-Job -Force | Remove-Job -Force }
Start-Job -Name "backend" -ScriptBlock { & .\.venv\Scripts\uvicorn main:app --host $using:BindHost --port $using:BindPort } | Out-Null
Start-Sleep -Seconds 2
npm run dev

Get-Job -Name backend | Stop-Job -Force -ErrorAction SilentlyContinue | Out-Null
Get-Job -Name backend | Remove-Job -Force -ErrorAction SilentlyContinue | Out-Null

