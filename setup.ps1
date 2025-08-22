# setup.ps1: MauEyeCare project environment setup script.
# - Installs Python and Node dependencies for backend and frontend.
# - Runs Alembic migrations (handles missing revision errors).
# - Optionally applies database seeds from seed.sql.
# Copy and run from the project root.

$ErrorActionPreference = "Stop"

Write-Host "========== MauEyeCare Setup Script ==========" -ForegroundColor Cyan

function Find-Directory($relativeName) {
    $dirs = Get-ChildItem -Path . -Directory -Recurse `
        | Where-Object { $_.Name -ieq $relativeName }
    if ($dirs.Count -eq 1) {
        return $dirs[0].FullName
    } elseif ($dirs.Count -gt 1) {
        # Prefer the directory at depth 1
        $firstLevel = $dirs | Where-Object { $_.Parent.FullName -eq (Get-Location).Path }
        if ($firstLevel.Count -ge 1) { return $firstLevel[0].FullName }
        return $dirs[0].FullName
    }
    else { return $null }
}

function Find-Backend {
    # Heuristics: Looks for folder containing alembic.ini, requirements.txt, app/main.py, or pyproject.toml
    $candidates = Get-ChildItem -Path . -Directory -Recurse | Where-Object {
        Test-Path "$($_.FullName)\alembic.ini" -or
        Test-Path "$($_.FullName)\requirements.txt" -or
        Test-Path "$($_.FullName)\pyproject.toml"
    }
    # Prioritize directories containing app/main.py as FastAPI entrypoint
    foreach ($dir in $candidates) {
        if (Test-Path "$($dir.FullName)\app\main.py" -or Test-Path "$($dir.FullName)\main.py") {
            return $dir.FullName
        }
    }
    if ($candidates) { return $candidates[0].FullName }
    throw "No backend directory found."
}

function Find-Frontend {
    # Looks for directory with package.json and vite.config.* files
    $candidates = Get-ChildItem -Path . -Directory -Recurse | Where-Object {
        Test-Path "$($_.FullName)\package.json"
    }
    foreach ($dir in $candidates) {
        $viteConfig = Get-ChildItem "$($dir.FullName)" -Filter "vite.config.*" -File
        if ($viteConfig) { return $dir.FullName }
    }
    if ($candidates) { return $candidates[0].FullName }
    throw "No frontend directory found."
}

$backendDir = Find-Backend
Write-Host "Found backend directory: $backendDir" -ForegroundColor Green

$frontendDir = Find-Frontend
Write-Host "Found frontend directory: $frontendDir" -ForegroundColor Green

Push-Location $backendDir

# 1. (Optional) Create virtual environment if not present
if (-not (Test-Path ".venv")) {
    Write-Host "Creating Python virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}
if (Test-Path ".venv") {
    $venvPython = ".venv\Scripts\python.exe"
    $pip = "$venvPython -m pip"
} else {
    # fallback to system Python
    $venvPython = "python"
    $pip = "python -m pip"
}

# 2. Install backend deps
Write-Host "Installing backend Python dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install -r requirements.txt
} elseif (Test-Path "pyproject.toml") {
    # Use pip or, if poetry present, prefer poetry
    if (Test-Path "poetry.lock" -or (Get-Command poetry -ErrorAction SilentlyContinue)) {
        & poetry install
    } else {
        & $venvPython -m pip install .
    }
} else {
    Write-Host "No requirements.txt or pyproject.toml found in backend." -ForegroundColor Red
}

# 3. Install Alembic if needed
try {
    & $venvPython -m pip show alembic | Out-Null
} catch {
    & $venvPython -m pip install alembic
}

# 4. Alembic migration with error recovery
if (Test-Path "alembic.ini") {
    Write-Host "Running Alembic migrations..." -ForegroundColor Yellow
    try {
        & $venvPython -m alembic upgrade head
        Write-Host "Alembic migrations completed." -ForegroundColor Green
    } catch {
        Write-Host "Alembic migration failed: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Message -match "Can't locate revision") {
            $response = Read-Host "Alembic revision missing. Attempt to reset migrations? (stamp database to current and reapply? y/n)"
            if ($response -eq "y") {
                & $venvPython -m alembic stamp head
                & $venvPython -m alembic upgrade head
                Write-Host "Alembic database pointer reset and re-applied."
            } else {
                throw "Migration failed due to missing revision; please resolve manually."
            }
        } else {
            throw $_.Exception
        }
    }
} else {
    Write-Host "No alembic.ini found; skipping migrations." -ForegroundColor Yellow
}

# 5. Database seed
if (Test-Path "seed.sql") {
    Write-Host "Seeding database from seed.sql..." -ForegroundColor Yellow
    # Try using psql (Postgres, common in FastAPI stacks)
    $psqlFound = Get-Command psql -ErrorAction SilentlyContinue
    if ($psqlFound) {
        # Read DB URI from env or alembic.ini
        $conn = $env:DATABASE_URL
        if (-not $conn -and (Test-Path ".env")) {
            $conn = ((Get-Content .env | Select-String -Pattern '^DATABASE_URL=')).ToString().Split("=",2)[1].Trim()
        }
        if (-not $conn -and (Test-Path "alembic.ini")) {
            $line = Select-String "sqlalchemy.url" alembic.ini
            if ($line) { $conn = $line -replace "sqlalchemy.url\s*=\s*", "" }
        }
        if ($conn) {
            & psql "$conn" -f seed.sql
            Write-Host "Seed applied via psql." -ForegroundColor Green
        } else {
            Write-Host "Could not locate DATABASE_URL for seeding. Please run manually." -ForegroundColor Yellow
        }
    } else {
        Write-Host "psql (Postgres CLI) not found in PATH. Please seed manually." -ForegroundColor Red
    }
} else {
    Write-Host "No seed.sql present, skipping seeding."
}

Pop-Location

# 6. Frontend dependency install
Push-Location $frontendDir
Write-Host "Installing frontend Node dependencies..." -ForegroundColor Yellow
if (Test-Path "package-lock.json") {
    npm ci
} else {
    npm install
}
Pop-Location

Write-Host "✅ MauEyeCare setup complete. Ready to run the servers!" -ForegroundColor Cyan
