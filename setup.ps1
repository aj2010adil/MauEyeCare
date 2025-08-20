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

Write-Host "Ensuring C++ Build Tools are installed (for Python packages)..." -ForegroundColor Yellow
Install-OrUpgradePackage visualstudio2022-workload-vctools ""

# Install PostgreSQL with retry logic
try {
    Write-Host "Attempting to install or upgrade PostgreSQL..." -ForegroundColor Yellow
    Install-OrUpgradePackage postgresql "--params '/Password:maueyecare'"
} catch {
    Write-Warning "PostgreSQL installation/upgrade failed. This can happen if a previous installation is corrupt."
    Write-Warning "Attempting to forcefully uninstall and reinstall PostgreSQL. This may affect other databases on your system."
    choco uninstall postgresql -fy
    Write-Host "Re-installing PostgreSQL..." -ForegroundColor Yellow
    choco install postgresql -y "--params '/Password:maueyecare'"
}

Write-Host "Verifying PostgreSQL service status..." -ForegroundColor Yellow
$maxRetries = 10
$retryDelaySeconds = 3
$pgService = $null

for ($i = 1; $i -le $maxRetries; $i++) {
    $pgService = Get-Service -Name "postgres*" -ErrorAction SilentlyContinue | Where-Object { $_.Name -like 'postgresql-x64-*' -or $_.DisplayName -like 'PostgreSQL Server*' -or $_.Name -like 'postgresql-*' } | Select-Object -First 1
    if ($pgService) {
        Write-Host "PostgreSQL service found." -ForegroundColor Green
        break
    }
    Write-Host "Waiting for PostgreSQL service to appear... (attempt $i of $maxRetries)" -ForegroundColor DarkGray
    Start-Sleep -Seconds $retryDelaySeconds
}

if (-not $pgService) {
    Write-Error "PostgreSQL service was not found after installation. Setup cannot continue."
    Write-Host "---" -ForegroundColor Yellow
    Write-Host "TROUBLESHOOTING:" -ForegroundColor Yellow
    Write-Host "1. Run 'choco list --local-only' to see if 'postgresql' is listed." -ForegroundColor Yellow
    Write-Host "2. Check Windows 'Services' to see if a PostgreSQL service exists with a different name." -ForegroundColor Yellow
    Write-Host "3. You may need to install PostgreSQL manually from https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

if ($pgService.Status -ne 'Running') {
    Write-Warning "PostgreSQL service is not running. Attempting to start it..."
    Start-Service -InputObject $pgService
    Start-Sleep -Seconds 5 # Give it a moment to start
    $pgService.Refresh()
    if ($pgService.Status -ne 'Running') {
        Write-Error "Failed to start the PostgreSQL service. Please check the Windows Event Viewer for details."
        exit 1
    }
}
Write-Host "PostgreSQL service is running." -ForegroundColor Green

Write-Host "Updating environment to find PostgreSQL..." -ForegroundColor Yellow
$pgBinPath = (Get-ChildItem -Path "$($env:ProgramFiles)\PostgreSQL\*\bin" -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
if (-not $pgBinPath) {
    $pgBinPath = (Get-ChildItem -Path "${env:ProgramFiles(x86)}\PostgreSQL\*\bin" -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
}
if ($pgBinPath -and !($env:Path -like "*$pgBinPath*")) {
    Write-Host "Adding PostgreSQL bin to PATH for this session: $pgBinPath"
    # Prepend to path to ensure it's found first
    $env:Path = "$pgBinPath;$($env:Path)"
}

Write-Host "Creating Python venv and installing requirements..." -ForegroundColor Yellow
if (!(Test-Path .venv)) { py -3 -m venv .venv }
& .\.venv\Scripts\pip install --upgrade pip
& .\.venv\Scripts\pip install -r requirements.txt

Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
if (Test-Path package.json) { npm install }

Write-Host "Configuring PostgreSQL..." -ForegroundColor Yellow

function Get-PsqlPath {
  $candidates = @(
    (Join-Path $env:ProgramFiles "PostgreSQL\**\bin\psql.exe"),
    (Join-Path ${env:ProgramFiles(x86)} "PostgreSQL\**\bin\psql.exe")
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
  # Test connection to PostgreSQL
  try {
    & $psqlExe -U $pgSuperUser -h $pgHost -p $pgPort -c "\q" 2>$null
    Write-Host "Successfully connected to PostgreSQL." -ForegroundColor Green
  } catch {
      Write-Error "Failed to connect to PostgreSQL. Please ensure the service is running and accessible."
      Write-Error "Connection details: Host=$pgHost, Port=$pgPort, User=$pgSuperUser"
      Write-Error "If password is not 'maueyecare', set it via the MAU_PG_SUPERPASS environment variable."
      # Clean up the password from the environment for security
      Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
      exit 1
  }

  try {
    & $psqlExe -U $pgSuperUser -h $pgHost -p $pgPort -c "CREATE USER maueyecare WITH PASSWORD 'maueyecare' CREATEDB;" | Out-Null
    Write-Host "Successfully created PostgreSQL user 'maueyecare'." -ForegroundColor Green
  } catch {
      if ($_.Exception.Message -like "*already exists*") { Write-Host "Skip: user 'maueyecare' already exists." -ForegroundColor DarkYellow }
      else { Write-Warning "Failed to create user 'maueyecare'. Error: $($_.Exception.Message)" }
  }
  try {
    & $psqlExe -U $pgSuperUser -h $pgHost -p $pgPort -c "CREATE DATABASE maueyecare OWNER maueyecare;" | Out-Null
    Write-Host "Successfully created PostgreSQL database 'maueyecare'." -ForegroundColor Green
  } catch {
      if ($_.Exception.Message -like "*already exists*") { Write-Host "Skip: database 'maueyecare' already exists." -ForegroundColor DarkYellow }
      else { Write-Warning "Failed to create database 'maueyecare'. Error: $($_.Exception.Message)" }
  }

  # Clean up the password from the environment for security
  Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
} else {
  Write-Warning "psql.exe not found in common locations or PATH. Skipping DB provisioning. Ensure database exists and update MAU_DB_* in environment if needed."
}

Write-Host "Opening Windows Firewall for ports 5173 (frontend) and 8000 (backend)..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "MauEyeCare Frontend" -Direction Inbound -Protocol TCP -LocalPort 5173 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null
New-NetFirewallRule -DisplayName "MauEyeCare Backend" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Private -ErrorAction SilentlyContinue | Out-Null

Write-Host "Creating documents directories..." -ForegroundColor Yellow
$baseDocRoot = Join-Path $env:USERPROFILE "Documents\MauEyeCare"
"prescriptions", "invoices", "lab_jobs", "uploads" | ForEach-Object {
    New-Item -ItemType Directory -Force -Path (Join-Path $baseDocRoot $_) | Out-Null
}

Write-Host "Running Alembic migrations..." -ForegroundColor Yellow
& .\.venv\Scripts\python -m alembic upgrade head

Write-Host "Bootstrapping default doctor account..." -ForegroundColor Yellow
Start-Job { & .\.venv\Scripts\python -c "import uvicorn,main; uvicorn.run(main.app, host='127.0.0.1', port=8001)" } | Out-Null
Start-Sleep -Seconds 5 # Give the server a moment to start
try {
    $bootstrapResult = Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8001/api/auth/bootstrap -ErrorAction Stop
    if ($bootstrapResult.created) {
        Write-Host "Successfully created default admin user." -ForegroundColor Green
    } else {
        Write-Host "Default admin user already exists, skipping creation." -ForegroundColor DarkYellow
    }
} catch {
    Write-Warning "Failed to bootstrap the default admin user. The backend server might have failed to start."
    Write-Warning "Error details: $($_.Exception.Message)"
    Write-Warning "You can try to create the user manually by running: .\.venv\Scripts\python.exe seed.py"
} finally { Get-Job | Stop-Job | Remove-Job -ErrorAction SilentlyContinue }

Write-Host "Setup complete." -ForegroundColor Green
