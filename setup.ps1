param(
  [switch]$Force
)

Write-Host "[MauEyeCare] Starting setup..." -ForegroundColor Cyan
$ErrorActionPreference = 'Stop'

function Install-ChocoIfMissing {
  if (!(Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Chocolatey..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
  }
}

function Install-OrUpgradePackage($name, $pkgArgs) {
  if ($Force -or !(choco list --local-only | Select-String -Pattern "^$name ")) {
    choco install $name -y $pkgArgs
  } else { choco upgrade $name -y $pkgArgs }
}

Install-ChocoIfMissing
Install-OrUpgradePackage python ""
Install-OrUpgradePackage nodejs-lts ""
Install-OrUpgradePackage postgresql "--params '/Password:maueyecare'"

Write-Host "Creating Python venv and installing requirements..." -ForegroundColor Yellow
if (!(Test-Path .venv)) { py -3 -m venv .venv }
& .\.venv\Scripts\pip install --upgrade pip
& .\.venv\Scripts\pip install -r requirements.txt

Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
if (Test-Path package.json) { npm install }

Write-Host "Configuring PostgreSQL..." -ForegroundColor Yellow
$env:PGPASSWORD = 'maueyecare'
$psql = "C:\\Program Files\\PostgreSQL\\*\\bin\\psql.exe"
$psqlExe = (Get-ChildItem $psql | Sort-Object FullName -Descending | Select-Object -First 1).FullName
& "$psqlExe" -U postgres -h 127.0.0.1 -c "CREATE USER maueyecare WITH PASSWORD 'maueyecare' CREATEDB;" 2>$null | Out-Null
& "$psqlExe" -U postgres -h 127.0.0.1 -c "CREATE DATABASE maueyecare OWNER maueyecare;" 2>$null | Out-Null

Write-Host "Opening Windows Firewall for ports 5173 (frontend) and 8000 (backend)..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "MauEyeCare Frontend" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -DisplayName "MauEyeCare Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null

Write-Host "Creating documents directories..." -ForegroundColor Yellow
$docRoot = Join-Path $env:USERPROFILE "Documents\MauEyeCare\prescriptions"
New-Item -ItemType Directory -Force -Path $docRoot | Out-Null

Write-Host "Running Alembic migrations..." -ForegroundColor Yellow
& .\.venv\Scripts\python -m alembic upgrade head

Write-Host "Bootstrapping default doctor account..." -ForegroundColor Yellow
Start-Job { & .\.venv\Scripts\python -c "import uvicorn,main; uvicorn.run(main.app, host='127.0.0.1', port=8001)" } | Out-Null
Start-Sleep -Seconds 3
try { Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8001/api/auth/bootstrap } catch {}
Get-Job | Stop-Job | Remove-Job

Write-Host "Setup complete." -ForegroundColor Green

