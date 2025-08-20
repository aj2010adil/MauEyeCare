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

function Get-PsqlPath {
  $candidates = @(
    Join-Path $env:ProgramFiles "PostgreSQL\**\bin\psql.exe" ,
    Join-Path ${env:ProgramFiles(x86)} "PostgreSQL\**\bin\psql.exe"
  )
  foreach ($glob in $candidates) {
    try {
      $files = Get-ChildItem -Path $glob -ErrorAction SilentlyContinue
      if ($files) { return ($files | Sort-Object FullName -Descending | Select-Object -First 1).FullName }
    } catch {}
  }
  $cmd = Get-Command psql -ErrorAction SilentlyContinue
  if ($cmd) { return $cmd.Source }
  return $null
}

$pgHost = $env:MAU_DB_HOST; if (-not $pgHost) { $pgHost = '127.0.0.1' }
$pgPort = $env:MAU_DB_PORT; if (-not $pgPort) { $pgPort = '5432' }
$pgSuperUser = $env:MAU_PG_SUPERUSER; if (-not $pgSuperUser) { $pgSuperUser = 'postgres' }

# The choco installer sets the postgres user password to 'maueyecare'.
# We need to set PGPASSWORD so psql can authenticate non-interactively.
if ($env:MAU_PG_SUPERPASS) { $env:PGPASSWORD = $env:MAU_PG_SUPERPASS } else { $env:PGPASSWORD = 'maueyecare' }

$psqlExe = Get-PsqlPath
if ($psqlExe) {
  try {
    # Removed `2>$null` so that errors are not suppressed and can be caught.
    & $psqlExe -U $pgSuperUser -h $pgHost -p $pgPort -c "CREATE USER maueyecare WITH PASSWORD 'maueyecare' CREATEDB;" | Out-Null
  } catch { Write-Host "Skip: user 'maueyecare' creation (user may already exist)." -ForegroundColor DarkYellow }
  try {
    & $psqlExe -U $pgSuperUser -h $pgHost -p $pgPort -c "CREATE DATABASE maueyecare OWNER maueyecare;" | Out-Null
  } catch { Write-Host "Skip: database 'maueyecare' creation (database may already exist)." -ForegroundColor DarkYellow }

  # Clean up the password from the environment for security
  Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
} else {
  Write-Warning "psql.exe not found in common locations or PATH. Skipping DB provisioning. Ensure database exists and update MAU_DB_* in environment if needed."
}

Write-Host "Opening Windows Firewall for ports 5173 (frontend) and 8000 (backend)..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "MauEyeCare Frontend" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -DisplayName "MauEyeCare Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null

Write-Host "Creating documents directories..." -ForegroundColor Yellow
$docRoot = Join-Path $env:USERPROFILE "Documents\MauEyeCare\prescriptions"
New-Item -ItemType Directory -Force -Path $docRoot | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE "Documents\MauEyeCare\invoices") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE "Documents\MauEyeCare\lab_jobs") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $env:USERPROFILE "Documents\MauEyeCare\uploads") | Out-Null

Write-Host "Running Alembic migrations..." -ForegroundColor Yellow
& .\.venv\Scripts\python -m alembic upgrade head

Write-Host "Bootstrapping default doctor account..." -ForegroundColor Yellow
Start-Job { & .\.venv\Scripts\python -c "import uvicorn,main; uvicorn.run(main.app, host='127.0.0.1', port=8001)" } | Out-Null
Start-Sleep -Seconds 3
try { Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8001/api/auth/bootstrap } catch {}
Get-Job | Stop-Job | Remove-Job

Write-Host "Setup complete." -ForegroundColor Green
