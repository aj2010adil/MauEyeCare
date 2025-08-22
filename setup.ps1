# setup.ps1 - MauEyeCare Project Environment Setup Script
# For the `windows_version4_all_feature` branch, August 2025
# Installs backend and frontend dependencies, runs Alembic migrations, optionally seeds the database.

Write-Host "`n---- MauEyeCare Setup Script Started ----`n"

# --- 1. Detect backend folder ---
$repoFolders = Get-ChildItem -Directory | Where-Object { $_.Name -notin @('.git', '.vscode', '.idea', 'node_modules', 'dist') }

$backendCandidates = @('backend', 'server', 'api')
$backendFolder = $null

foreach ($candidate in $backendCandidates) {
    $found = $repoFolders | Where-Object { $_.Name -eq $candidate }
    if ($found) {
        $backendFolder = $found.FullName
        break
    }
}

if (-not $backendFolder) {
    # Fallback: search for a folder containing main.py and alembic.ini
    foreach ($folder in $repoFolders) {
        if (Test-Path (Join-Path $folder.FullName 'app\main.py') -or Test-Path (Join-Path $folder.FullName 'main.py')) {
            if (Test-Path (Join-Path $folder.FullName 'alembic.ini')) {
                $backendFolder = $folder.FullName
                break
            }
        }
    }
}

if (-not $backendFolder) {
    Write-Error "Could not locate backend folder. Please ensure it is named 'backend' or contains 'main.py' and 'alembic.ini'. Exiting..."
    exit 1
}

Write-Host "📦 Backend detected: $backendFolder"

# --- 2. Detect frontend folder ---
$frontendCandidates = @('frontend', 'client', 'web')
$frontendFolder = $null

foreach ($candidate in $frontendCandidates) {
    $found = $repoFolders | Where-Object { $_.Name -eq $candidate }
    if ($found -and (Test-Path (Join-Path $found.FullName 'package.json'))) {
        $frontendFolder = $found.FullName
        break
    }
}

if (-not $frontendFolder) {
    # Fallback: search for package.json
    foreach ($folder in $repoFolders) {
        if (Test-Path (Join-Path $folder.FullName 'package.json')) {
            $frontendFolder = $folder.FullName
            break
        }
    }
}

if (-not $frontendFolder) {
    Write-Error "Could not locate frontend folder. Please ensure it contains 'package.json'. Exiting..."
    exit 1
}

Write-Host "📦 Frontend detected: $frontendFolder"

# --- 3. Install backend dependencies (Python) ---
Write-Host "`n---- Installing backend (Python) dependencies ----"
Push-Location $backendFolder

if (Test-Path 'requirements.txt') {
    Write-Host "Installing Python dependencies from requirements.txt ..."
    try {
        pip install -r requirements.txt
    }
    catch {
        Write-Error "pip install failed. Please ensure Python and pip are installed and on your PATH."
        Pop-Location
        exit 1
    }
} else {
    Write-Warning "No requirements.txt found in $backendFolder. Skipping Python dependency installation."
}

# --- 4. Run Alembic migrations ---
if (Test-Path 'alembic.ini') {
    # Remove .pyc and orphaned migration folders if needed (optional, but good practice in dev)
    Write-Host "`nRunning Alembic migrations ..."
    try {
        alembic upgrade head
        if ($LASTEXITCODE -ne 0) {
            Write-Warning "Alembic migration failed. Please check if any migration script is missing (e.g., '20250821_fix_spectacles_schema')."
            Pop-Location
            exit 1
        }
    }
    catch {
        Write-Error "Alembic command not found or failed. Ensure Alembic is installed in your Python environment."
        Pop-Location
        exit 1
    }
} else {
    Write-Error "alembic.ini not found in $backendFolder. Cannot apply migrations!"
    Pop-Location
    exit 1
}

# --- 5. Seed the database (optional) ---
$seedSql = Join-Path $backendFolder 'seed.sql'
if (Test-Path $seedSql) {
    Write-Host "`nSeeding the database from seed.sql ..."
    # Load .env if available for credentials
    $envFile = Join-Path $backendFolder '.env'
    $dbUrl = $null
    if (Test-Path $envFile) {
        $lines = Get-Content $envFile
        foreach ($line in $lines) {
            if ($line -match 'DATABASE_URL\s*=\s*(.+)') {
                $dbUrl = $Matches[1].Trim()
            }
        }
    }
    # If DATABASE_URL found, parse protocol
    if ($dbUrl) {
        if ($dbUrl -match '^postgresql://') {
            # Use psql
            $psqlPath = Get-Command psql -ErrorAction SilentlyContinue
            if ($psqlPath) {
                Write-Host "Using psql for seeding (PostgreSQL detected)."
                $env:DATABASE_URL = $dbUrl
                psql $dbUrl -f $seedSql
            } else {
                Write-Host "psql not found in PATH. Please install PostgreSQL Client Tools."
            }
        } else {
            Write-Warning "Unrecognized DATABASE_URL protocol. Please manually seed the database."
        }
    } else {
        Write-Warning "No DATABASE_URL found. Cannot automatically seed; please seed manually."
    }
} else {
    Write-Host "No seed.sql found in $backendFolder. Skipping seeding step."
}

Pop-Location

# --- 6. Install frontend dependencies (Node/NPM) ---
Write-Host "`n---- Installing frontend (Node) dependencies ----"
Push-Location $frontendFolder

if (Test-Path 'package.json') {
    Write-Host "Installing Node.js dependencies via npm install ..."
    try {
        npm install
    }
    catch {
        Write-Error "npm install failed. Please ensure Node.js and npm are installed and on your PATH."
        Pop-Location
        exit 1
    }
} else {
    Write-Warning "No package.json found in $frontendFolder. Skipping Node.js dependency installation."
}

Pop-Location

Write-Host "`n✅ MauEyeCare setup complete. Ready to launch servers with run.ps1!`n"

exit 0
