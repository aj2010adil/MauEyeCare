<#
.SYNOPSIS
    Diagnoses the MauEyeCare development environment for common setup issues.
.PARAMETER FixCommon
    Attempts to automatically fix common issues like a missing .env file.
#>
param (
    [switch]$FixCommon,
    [switch]$AutoFix
)

$ErrorActionPreference = 'SilentlyContinue'
$Success = $true

function Test-Result {
    param([bool]$Condition, [string]$Message)
    if ($Condition) {
        Write-Host "  [ OK ]  $Message" -ForegroundColor Green
    } else {
        Write-Host "  [FAIL]  $Message" -ForegroundColor Red
        $script:Success = $false
    }
}

function Write-Warning-Line {
    param([string]$Message)
    Write-Host "  [WARN]  $Message" -ForegroundColor Yellow
}

Write-Host "[MauEyeCare Health Check]" -ForegroundColor Cyan

# --- Prerequisite Checks ---
Write-Host "1. Checking prerequisites..."
Test-Result (Get-Command choco) "Chocolatey is installed."
Test-Result (Get-Command python) "Python is installed."
Test-Result (Get-Command node) "Node.js is installed."

# --- Project Structure Checks ---
Write-Host "2. Checking project structure..."
Test-Result (Test-Path .\.venv) "Python virtual environment (.venv) exists."
Test-Result (Test-Path .\node_modules) "Node.js dependencies (node_modules) exist."

$envFileExists = Test-Path .\.env
if (-not $envFileExists -and $FixCommon) {
    Write-Host "  -  .env file not found. Attempting to fix..." -ForegroundColor Yellow
    if (Test-Path .\.env.example) {
        Copy-Item .\.env.example .\.env
        $envFileExists = Test-Path .\.env
        if ($envFileExists) {
            Write-Host "  -  Successfully created .env from .env.example." -ForegroundColor Green
        }
    }
}
Test-Result $envFileExists ".env file is present."
if ($envFileExists) {
    $content = Get-Content .\.env
    if ($content -match 'your_super_secret_random_string_for_jwt') {
        Write-Warning-Line "Default JWT secret is in use. Generate a new one for security."
    }
}

# --- PostgreSQL Checks ---
Write-Host "3. Checking PostgreSQL..."
$pgService = Get-Service -Name "postgres*" | Where-Object { $_.Name -like 'postgresql-x64-*' -or $_.DisplayName -like 'PostgreSQL Server*' -or $_.Name -like 'postgresql-*' } | Select-Object -First 1
Test-Result ($pgService) "PostgreSQL service is installed."
if ($pgService) {
    Test-Result ($pgService.Status -eq 'Running') "PostgreSQL service is running."
}

# Find psql.exe
$psqlExe = $null
$psqlCmd = Get-Command psql -ErrorAction SilentlyContinue
if ($psqlCmd) {
    $psqlExe = $psqlCmd.Source
} else {
    # Fallback to searching common paths if not in PATH
    $pgBinPath = (Get-ChildItem -Path "${env:ProgramFiles}\PostgreSQL\*\bin" | Select-Object -First 1).FullName
    if (-not $pgBinPath -and (Test-Path "${env:ProgramFiles(x86)}")) {
        $pgBinPath = (Get-ChildItem -Path "${env:ProgramFiles(x86)}\PostgreSQL\*\bin" | Select-Object -First 1).FullName
    }
    if ($pgBinPath) { $psqlExe = Join-Path $pgBinPath "psql.exe" }
}

Test-Result ($psqlExe -and (Test-Path $psqlExe)) "psql.exe command-line tool found."

if ($psqlExe) {
    # Load .env variables for connection
    if (Test-Path .\.env) {
        Get-Content .\.env | ForEach-Object {
            if ($_ -match '^\s*#') { return } # Skip comments
            if ($_ -match '^\s*(?<name>[\w_]+)\s*=\s*(?<value>.*)') {
                $value = $Matches.value.Trim()
                if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
                    $value = $value.Substring(1, $value.Length - 2)
                }
                Set-Content "env:\$($Matches.name)" $value
            }
        }
    }
    $pgHost = $env:MAU_DB_HOST; if (-not $pgHost) { $pgHost = '127.0.0.1' }
    $pgPort = $env:MAU_DB_PORT; if (-not $pgPort) { $pgPort = '5432' }
    $pgUser = $env:MAU_DB_USER; if (-not $pgUser) { $pgUser = 'maueyecare' }
    $pgDb = $env:MAU_DB_NAME; if (-not $pgDb) { $pgDb = 'maueyecare' }
    $env:PGPASSWORD = $env:MAU_DB_PASSWORD; if (-not $env:PGPASSWORD) { $env:PGPASSWORD = 'maueyecare' }
    Write-Host "Testing PostgreSQL connection: user=$pgUser db=$pgDb host=$pgHost port=$pgPort" -ForegroundColor Yellow

    $connTest = & $psqlExe -U $pgUser -h $pgHost -p $pgPort -d $pgDb -c "\q"
    Test-Result ($LASTEXITCODE -eq 0) "Can connect to the '$pgDb' database."

    if ($LASTEXITCODE -eq 0) {
        $userCount = (& $psqlExe -U $pgUser -h $pgHost -p $pgPort -d $pgDb -t -c "SELECT COUNT(*) FROM users;").Trim()
        Test-Result ($userCount -gt 0) "The 'users' table contains data (found $userCount users)."
    }
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

# --- Backend API Check ---
Write-Host "4. Checking backend API health..."
$pythonExe = ".\.venv\Scripts\python.exe"
if (Test-Path $pythonExe) {
    Write-Host "  -  Starting temporary backend server on port 8002..." -ForegroundColor DarkGray
    $job = Start-Job -ScriptBlock {
        param($python)
        & $python -m uvicorn main:app --host 127.0.0.1 --port 8002
    } -ArgumentList $pythonExe

    Start-Sleep -Seconds 5 # Give it time to start up

    $healthCheckSuccess = $false
    try {
        $response = Invoke-RestMethod -Uri http://127.0.0.1:8002/api/health -Method Get -TimeoutSec 5
        if ($response.status -eq 'ok') {
            $healthCheckSuccess = $true
        }
    } catch {
        # Error is expected if it fails, we just check the success flag
    } finally {
        Stop-Job $job | Remove-Job -Force
    }

    Test-Result $healthCheckSuccess "Backend API is healthy and responding."
} else { Test-Result $false "Python executable not found in .venv. Cannot test backend." }

# --- Port and Migration Checks ---
Write-Host "5. Checking ports and migrations..."

function Get-PortConflicts {
    param([int]$Port)
    $results = @()
    try {
        $lines = netstat -ano -p TCP | Select-String -Pattern (":$Port\s")
        foreach ($l in $lines) {
            $parts = ($l -split "\s+") | Where-Object { $_ -ne '' }
            if ($parts.Length -ge 5) {
                $pid = $parts[-1]
                try { $proc = Get-Process -Id $pid -ErrorAction Stop; $results += [PSCustomObject]@{ PID=$pid; Name=$proc.ProcessName } } catch {}
            }
        }
    } catch {}
    return $results | Sort-Object PID -Unique
}

# Check common ports 8000 (backend) and 5173 (frontend)
foreach ($p in 8000,5173) {
    $conf = Get-PortConflicts -Port $p
    if ($conf.Count -gt 0) {
        Write-Host "  [WARN]  Port $p is in use by:" -ForegroundColor Yellow
        $conf | ForEach-Object { Write-Host ("          PID {0} - {1}" -f $_.PID, $_.Name) -ForegroundColor Yellow }
        if ($AutoFix) {
            Write-Host "  -  AutoFix enabled: attempting to stop conflicting processes on port $p" -ForegroundColor DarkYellow
            $conf | ForEach-Object { try { Stop-Process -Id $_.PID -Force -ErrorAction SilentlyContinue } catch {} }
        }
    } else {
        Write-Host "  [ OK ]  No conflicts detected on port $p" -ForegroundColor Green
    }
}

# Alembic migration status
$pythonExe = ".\.venv\Scripts\python.exe"
if (Test-Path $pythonExe) {
    try {
        $headsOut = & $pythonExe -m alembic heads 2>&1
        $currOut = & $pythonExe -m alembic current 2>&1
        $revRegex = "[0-9a-f]{6,}"
        $heads = [System.Text.RegularExpressions.Regex]::Matches($headsOut, $revRegex) | ForEach-Object { $_.Value } | Select-Object -Unique
        $currs = [System.Text.RegularExpressions.Regex]::Matches($currOut, $revRegex) | ForEach-Object { $_.Value } | Select-Object -Unique
        if ($currs.Count -eq 0) {
            Write-Host "  [WARN]  Database not stamped or empty migration state." -ForegroundColor Yellow
            if ($AutoFix) {
                Write-Host "  -  AutoFix: applying migrations (upgrade head)" -ForegroundColor DarkYellow
                & $pythonExe -m alembic upgrade head | Out-Null
            }
        } elseif ($heads -notcontains $currs[-1]) {
            Write-Host "  [WARN]  Database not at latest migration head." -ForegroundColor Yellow
            if ($AutoFix) {
                Write-Host "  -  AutoFix: upgrading database to head" -ForegroundColor DarkYellow
                & $pythonExe -m alembic upgrade head | Out-Null
            }
        } else {
            Write-Host "  [ OK ]  Database is at latest migration head." -ForegroundColor Green
        }
    } catch {
        Write-Host "  [WARN]  Unable to determine Alembic status: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# --- Summary ---
Write-Host "---"
if ($script:Success) {
    Write-Host "[PASS] System health check passed." -ForegroundColor Green
} else {
    Write-Host "[FAIL] System health check failed. Please review the errors above." -ForegroundColor Red
    $response = Read-Host "Some checks failed. Would you like to try and fix this by re-running the main setup script? (y/n)"
    if ($response -eq 'y') {
        Write-Host "Re-running setup.ps1..." -ForegroundColor Yellow
        
        # Check for admin rights, as they are required for choco install
        if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
            Write-Warning "This script needs to be run as an Administrator to execute setup.ps1. Please re-run your terminal as Administrator and try again."
            exit 1
        }

        $setupScriptPath = Join-Path $PSScriptRoot "..\setup.ps1"
        if (Test-Path $setupScriptPath) {
            & $setupScriptPath
        } else { Write-Error "Could not find setup.ps1 at $setupScriptPath" }
    }
}