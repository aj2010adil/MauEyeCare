# run.ps1
# Cleans pytest cache, detects FastAPI entrypoint, launches backend/Frontend in parallel, and opens browser to frontend.

Write-Host "=== MauEyeCare Run Script ===" -ForegroundColor Yellow

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

# Helper: Find FastAPI main file (returns relative import path, e.g., app.main)
function Find-FastAPIEntrypoint($backendRoot) {
    $candidates = Get-ChildItem -Path $backendRoot -Recurse -Include "main.py" -File | ForEach-Object {
        $content = Get-Content $_.FullName -Encoding UTF8 -ErrorAction SilentlyContinue
        if ($content -match 'app\s*=\s*FastAPI\(') { $_ }
    }
    if ($candidates) {
        $mainPy = $candidates | Sort-Object { $_.FullName.Length } | Select-Object -First 1
        $relPath = $mainPy.FullName.Substring($backendRoot.Length).TrimStart('\','/')
        # Remove extension and convert path e.g. app\main.py -> app.main
        $importName = $relPath -replace '[\\/]', '.' -replace '\.py$', ''
        $importName = $importName.Trim('.') # Defensive
        return @{ File=$mainPy.FullName; Import=$importName }
    } else {
        return $null
    }
}

# --- Detect backend, frontend directories ---
$backendDir = Find-FolderWithFile "." "requirements.txt"
if (-not $backendDir) { $backendDir = Find-FolderWithFile "." "alembic.ini" }
if (-not $backendDir) { Write-Error "❌ Backend not found. Aborting run."; exit 10 }

$frontendDir = Find-FolderWithFile "." "package.json"
if ($frontendDir) {
    $viteConfig = Get-ChildItem -Path $frontendDir -Filter "vite.config.*" -ErrorAction SilentlyContinue
    if (-not $viteConfig) {
        Write-Warning "⚠️ package.json found at $frontendDir but vite.config.* missing. Check your frontend structure."
    }
} else { Write-Warning "⚠️ Frontend folder not found. Frontend server launch will be skipped." }

# --- Clean up pytest cache ---
Write-Host "`n[1/4] Removing backend .pytest_cache..." 
Push-Location $backendDir
try {
    Remove-Item ".pytest_cache" -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "✅ .pytest_cache cleaned."
} catch {
    Write-Warning "Could not remove .pytest_cache (may not exist)."
}
Pop-Location

# --- Detect FastAPI entrypoint ---
Write-Host "`n[2/4] Detecting FastAPI main file location..."
$faEntry = Find-FastAPIEntrypoint $backendDir
if (-not $faEntry) {
    Write-Error "❌ Could not find FastAPI app entrypoint (no main.py containing 'app = FastAPI()') in backend. Aborting."
    exit 11
}
Write-Host "✓ Found FastAPI main at '$($faEntry.File)', importable as '$($faEntry.Import)'"

# --- Start backend (uvicorn FastAPI) in background job ---
Write-Host "`n[3/4] Starting backend API server (Uvicorn)..."
Push-Location $backendDir
$backendJob = Start-Job -Name "MauEyeCare_Backend" -ScriptBlock {
    param($importName)
    python -m uvicorn "$importName:app" --host 0.0.0.0 --port 8000 --reload
} -ArgumentList $faEntry.Import
Pop-Location
Start-Sleep -Seconds 2
if ($backendJob.State -eq "Failed") {
    Write-Error "❌ Failed to start backend server. Use 'Get-Job' to troubleshoot."
    Receive-Job -Id $backendJob.Id
    Remove-Job -Id $backendJob.Id
    exit 12
} else {
    Write-Host "✅ Backend API running as job (Get-Job -Name MauEyeCare_Backend)."
}

# --- Start frontend (Vite) in background job ---
if ($frontendDir) {
    Write-Host "`n[4/4] Starting frontend (Vite) dev server..."
    Push-Location $frontendDir
    $frontendJob = Start-Job -Name "MauEyeCare_Frontend" -ScriptBlock {
        npm run dev
    }
    Pop-Location
    Write-Host "✅ Frontend dev server running as job (Get-Job -Name MauEyeCare_Frontend)."

    # Wait briefly, then open browser
    Start-Sleep -Seconds 7
    try {
        $vitePort = 5173
        $viteUrl = "http://localhost:$vitePort"
        Write-Host "Opening browser to $viteUrl ..."
        Start-Process $viteUrl
    } catch {
        Write-Warning "⚠️ Could not open browser automatically. Please open http://localhost:5173 manually."
    }
} else {
    Write-Host "ℹ️ No frontend present, skipping frontend start and browser launch."
}

Write-Host "`n---"
Write-Host "Servers are running in background jobs. To stop, use:"
Write-Host "  Stop-Job -Name MauEyeCare_Backend"
Write-Host "  Stop-Job -Name MauEyeCare_Frontend"
Write-Host "`nUse 'Get-Job' to see status and 'Receive-Job -Id <jobId>' to view output."
Write-Host "=== App Run Complete ===" -ForegroundColor Green
exit 0
