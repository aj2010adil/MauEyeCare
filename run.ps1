# run.ps1: MauEyeCare dev run script.
# - Cleans up backend test caches.
# - Locates FastAPI entrypoint and starts backend server.
# - Starts frontend vite dev server.
# - Opens browser to frontend.
# Recommended: run from the repo root.

$ErrorActionPreference = "Stop"

Write-Host "========== MauEyeCare Run Script ==========" -ForegroundColor Green

function Find-Backend {
    $candidates = Get-ChildItem -Path . -Directory -Recurse | Where-Object {
        Test-Path "$($_.FullName)\alembic.ini" -or
        Test-Path "$($_.FullName)\requirements.txt" -or
        Test-Path "$($_.FullName)\pyproject.toml"
    }
    foreach ($dir in $candidates) {
        if (Test-Path "$($dir.FullName)\app\main.py" -or Test-Path "$($dir.FullName)\main.py") {
            return $dir.FullName
        }
    }
    if ($candidates) { return $candidates[0].FullName }
    throw "No backend directory found."
}

function Find-Frontend {
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

# 1. Clean pytest and build caches in backend
Push-Location $backendDir
foreach ($cache in @(".pytest_cache", "dist", ".mypy_cache")) {
    if (Test-Path $cache) {
        Write-Host "Removing $cache..." -ForegroundColor Yellow
        Remove-Item $cache -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# 2. Find FastAPI main.py relative path (app.main:app or main:app)
$mainFile = $null; $appModule = $null
if (Test-Path "app\main.py") {
    $mainFile = "app\main.py"
    $appModule = "app.main:app"
} elseif (Test-Path "main.py") {
    $mainFile = "main.py"
    $appModule = "main:app"
} else {
    $candidates = Get-ChildItem -Recurse -Filter "main.py"
    if ($candidates) {
        $relMain = $candidates[0].FullName.Substring($backendDir.Length+1)
        $mainFile = $relMain
        # Convert path to Python module string
        $mod = $relMain -replace "\\","."
        $mod = $mod -replace ".py$",""
        $appModule = "$mod:app"
    }
}
if (-not $appModule) {
    throw "Could not locate FastAPI main.py entrypoint."
}

Write-Host "FastAPI entrypoint: $appModule (file: $mainFile)" -ForegroundColor Green

# 3. Activate virtual environment (if present)
if (Test-Path ".venv") {
    $uvicornCmd = ".venv\Scripts\python.exe -m uvicorn $appModule --reload"
} else {
    $uvicornCmd = "python -m uvicorn $appModule --reload"
}

Pop-Location

# 4. Start backend server in new terminal
Write-Host "Starting backend FastAPI server..." -ForegroundColor Yellow
Start-Process -NoNewWindow -WorkingDirectory $backendDir powershell "-NoExit", "-Command", $uvicornCmd

# 5. Start frontend dev server in new terminal
Write-Host "Starting frontend Vite server..." -ForegroundColor Yellow
Start-Process -NoNewWindow -WorkingDirectory $frontendDir powershell "-NoExit", "-Command", "npm run dev"

# 6. Detect frontend port from vite.config.*, fallback to 5173
$frontendPort = 5173
Push-Location $frontendDir
$viteConfig = Get-ChildItem . -Filter "vite.config.*" -File | Select-Object -First 1
if ($viteConfig) {
    $configText = Get-Content $viteConfig.FullName
    $portMatch = $configText | Select-String -Pattern "port\s*:\s*(\d+)"
    if ($portMatch) {
        $portNumber = ($portMatch.Matches[0].Groups[1].Value)
        if ([int]::TryParse($portNumber, [ref]$null)) {
            $frontendPort = [int]$portNumber
        }
    }
}
Pop-Location

# 7. Open browser to frontend
Start-Sleep -Seconds 3 # Wait for frontend dev server
$frontendUrl = "http://localhost:$frontendPort"
Write-Host "Opening browser to $frontendUrl ..." -ForegroundColor Green
Start-Process $frontendUrl

Write-Host "`nAll servers started. Backend and frontend are each running in their own terminals."
Write-Host "Press Ctrl+C in any terminal to terminate that dev server instance when done."
