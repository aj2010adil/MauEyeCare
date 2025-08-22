# setup.ps1
# Fully automates Python and Node dependency installation, Alembic migrations, and attempts to run DB seed.sql if present.
# Works with dynamic MauEyeCare folder structure and robust error handling.

Write-Host "=== MauEyeCare Setup Script ===" -ForegroundColor Cyan

# Helper: Find folder containing a marker file (e.g., requirements.txt for backend)
function Find-FolderWithFile($root, $filename) {
    $result = Get-ChildItem -Path $root -Recurse -File -Filter $filename -ErrorAction SilentlyContinue |
        Select-Object -First 1
    if ($result) {
        return $result.Directory.FullName
    } else {
        return $null
    }
}

# Find backend (looks for requirements.txt or alembic.ini)
$backendDir = Find-FolderWithFile "." "requirements.txt"
if (-not $backendDir) {
    $backendDir = Find-FolderWithFile "." "alembic.ini"
}
if (-not $backendDir) {
    Write-Error "❌ Could not find backend folder containing requirements.txt or alembic.ini. Aborting setup." 
    exit 2
}

# Find frontend (looks for package.json and vite.config.*)
$frontendDir = Find-FolderWithFile "." "package.json"
if ($frontendDir) {
    $viteConfig = Get-ChildItem -Path $frontendDir -Filter "vite.config.*" -ErrorAction SilentlyContinue
    if (-not $viteConfig) {
        Write-Warning "⚠️ package.json found at $frontendDir but vite.config.* missing. Check your frontend structure."
    }
} else {
    Write-Warning "⚠️ No package.json found in tree. Frontend install will be skipped."
}

# --- Install Python requirements ---
Write-Host "`n[1/4] Installing backend requirements in `"$backendDir`"..."
Push-Location $backendDir
try {
    if (Test-Path ".venv" -PathType Container) {
        Write-Host "Activating found Python venv..."
        $venvScripts = Join-Path ".venv" "Scripts"
        $activateScript = Join-Path $venvScripts "Activate.ps1"
        if (Test-Path $activateScript) {
            & $activateScript
        } else {
            Write-Warning "⚠️ .venv\\Scripts\\Activate.ps1 not found. Continuing without venv."
        }
    }
    pip install --upgrade pip
    pip install -r requirements.txt
    Write-Host "✅ Python packages installed successfully."
} catch {
    Write-Error "❌ Failed to install Python requirements: $($_.Exception.Message)"
    exit 3
}
Pop-Location

# --- Install Node.js frontend dependencies ---
if ($frontendDir) {
    Write-Host "`n[2/4] Installing frontend dependencies in `"$frontendDir`"..."
    Push-Location $frontendDir
    try {
        if (Test-Path "package-lock.json") {
            npm ci
        } else {
            npm install
        }
        Write-Host "✅ Node packages installed successfully."
    } catch {
        Write-Error "❌ Failed to install Node dependencies: $($_.Exception.Message)"
        exit 4
    }
    Pop-Location
} else {
    Write-Warning "⚠️ Frontend directory not found. Skipping npm install."
}

# --- Run Alembic migrations ---
Write-Host "`n[3/4] Running Alembic migrations..."
Push-Location $backendDir
try {
    $alembicIni = Join-Path $backendDir "alembic.ini"
    if (-not (Test-Path $alembicIni -PathType Leaf)) {
        Write-Error "❌ alembic.ini not found in $backendDir. Cannot run migrations."
        exit 5
    }
    $alembicOut = & alembic -c $alembicIni upgrade head 2>&1
    if ($LASTEXITCODE -ne 0) {
        if ($alembicOut -match "Can't locate revision identified by '20250821_fix_spectacles_schema'") {
            Write-Warning "⚠️ Migration failed: missing revision '20250821_fix_spectacles_schema'. Attempting Alembic recovery with 'stamp head'..."
            & alembic -c $alembicIni stamp head
            & alembic -c $alembicIni upgrade head
            if ($LASTEXITCODE -ne 0) {
                Write-Error "❌ Alembic migration recovery failed. Manual intervention required."
                exit 6
            }
        } else {
            Write-Error "❌ Alembic migration failed: $alembicOut"
            exit 6
        }
    }
    Write-Host "✅ Alembic migrations applied."
} catch {
    Write-Error "❌ Exception during Alembic migration: $($_.Exception.Message)"
    exit 7
}
Pop-Location

# --- Run seed.sql if present ---
Write-Host "`n[4/4] Attempting to seed DB with seed.sql (if present)..."
$seedPath = Join-Path $backendDir "seed.sql"
if (Test-Path $seedPath -PathType Leaf) {
    # Try to parse connection string from .env
    $envPath = Join-Path $backendDir ".env"
    $dbConnLine = ""
    if (Test-Path $envPath) {
        $dbConnLine = Get-Content $envPath | Where-Object { $_ -match "^DATABASE_URL\s*=" }
    }
    if ($dbConnLine -match "postgres://") {
        $pgUri = $dbConnLine -replace "DATABASE_URL\s*=\s*", ""
        Write-Host "Seeding database using psql and parsed connection string (may require configuration)..."
        try {
            & psql $pgUri -f $seedPath
            Write-Host "✅ Database seeded."
        } catch {
            Write-Warning "⚠️ Could not seed with psql: $($_.Exception.Message). Seed may require manual execution."
        }
    } else {
        Write-Warning "⚠️ Could not find a suitable postgres DATABASE_URL in .env. Skipping automatic seeding."
    }
} else {
    Write-Host "ℹ️ No seed.sql present. Skipping database seeding."
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Green
exit 0
