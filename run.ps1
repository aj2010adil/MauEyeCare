param(
  [string]$BindHost = '127.0.0.1',
  [int]$BindPort = 8001
)

Write-Host "[MauEyeCare] Starting backend (${BindHost}:${BindPort}) and frontend..." -ForegroundColor Cyan
$ErrorActionPreference = 'Stop'

if (!(Test-Path .venv)) { Write-Error ".venv not found. Run scripts/setup.ps1 first."; exit 1 }

function Get-LocalIPv4 {
  $ips = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notmatch '^169\.254\.' -and $_.IPAddress -notmatch '^127\.' }
  $ip = ($ips | Select-Object -First 1).IPAddress
  if ([string]::IsNullOrWhiteSpace($ip)) { $ip = '127.0.0.1' }
  return $ip
}

$ip = Get-LocalIPv4
Write-Host "LAN IP (frontend): http://$ip:5173" -ForegroundColor Yellow
Write-Host "Backend health: http://127.0.0.1:${BindPort}/api/health" -ForegroundColor Yellow

if (Get-Job -Name backend -ErrorAction SilentlyContinue) {
  try { Get-Job -Name backend | Stop-Job -ErrorAction SilentlyContinue } catch {}
  try { Get-Job -Name backend | Remove-Job -ErrorAction SilentlyContinue } catch {}
}
Start-Job -Name "backend" -ScriptBlock { & .\.venv\Scripts\uvicorn main:app --host $using:BindHost --port $using:BindPort } | Out-Null
Start-Sleep -Seconds 2
npm run dev

try { Get-Job -Name backend | Stop-Job -ErrorAction SilentlyContinue | Out-Null } catch {}
try { Get-Job -Name backend | Remove-Job -ErrorAction SilentlyContinue | Out-Null } catch {}

