# run.ps1 - MauEyeCare Project Development Run Script
# For the `windows_version4_all_feature` branch, August 2025
# Launches backend (FastAPI) and frontend (Vite) dev servers, clears .pytest_cache.

Write-Host "`n---- MauEyeCare Run Script Started ----`n"

# --- 1. Detect backend and frontend folders (same logic as setup.ps1) ---
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
    foreach ($folder in $repoFolders) {
        if (Test-Path (Join-Path $folder.FullName 'app\main.py') -or Test-Path (Join-Path $folder.FullName 'main.py')) {
            $backendFolder = $folder.FullName
            break
        }
    }
}
if (-not $backendFolder) {
    Write-Error "Could not locate backend folder. Exiting..."
    exit 1
}
Write-Host "📦 Backend detected: $backendFolder"

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
    foreach ($folder in $repoFolders) {
        if (Test-Path (Join-Path $folder.FullName 'package.json')) {
            $frontendFolder = $folder.FullName
            break
        }
    }
}
if (-not $frontendFolder) {
    Write-Error "Could not locate frontend folder. Exiting..."
    exit 1
}
Write-Host "📦 Frontend detected: $frontendFolder"

# --- 2. Clear .pytest_cache (if present) ---
$pytestCache = Join-Path $backendFolder '.pytest_cache'
if (Test-Path $pytestCache) {
    Write-Host "`nRemoving existing .pytest_cache ..."
    try {
        Remove-Item -Recurse -Force $pytestCache
    }
    catch {
        Write-Warning "Failed to remove .pytest_cache (possibly locked)."
    }
}

# --- 3. Detect FastAPI entrypoint ---
$mainPy = $null
$appDir = Join-Path $backendFolder 'app'
# Try backend/app/main.py then backend/main.py
if (Test-Path (Join-Path $appDir 'main.py')) {
    $mainPy = (Join-Path $appDir 'main.py')
    $uvicornModule = 'app.main:app'
    $workingDir = $backendFolder
} elseif (Test-Path (Join-Path $backendFolder 'main.py')) {
    $mainPy = (Join-Path $backendFolder 'main.py')
    $uvicornModule = 'main:app'
    $workingDir = $backendFolder
} else {
    Write-Error "Could not find backend app main.py. Please ensure your FastAPI entrypoint exists."
    exit 1
}

Write-Host "`n▶️ FastAPI entrypoint: $uvicornModule"

# --- 4. Launch backend (FastAPI) server ---
Write-Host "`nLaunching backend server (`uvicorn`) ..."

# Start backend in a new PowerShell window for developer convenience
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$workingDir'; uvicorn $uvicornModule --reload --port 8000" -WindowStyle Minimized

# --- 5. Launch frontend (Vite) server ---
Write-Host "`nLaunching frontend dev server (npm run dev) ..."
Push-Location $frontendFolder
if (Test-Path 'package.json') {
    # Figure out which npm script starts Vite; assume 'dev' is present
    $pkgJson = Get-Content 'package.json' | Out-String | ConvertFrom-Json
    if ($pkgJson.scripts.dev) {
        Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendFolder'; npm run dev" -WindowStyle Minimized
    } else {
        Write-Error "No 'dev' script found in package.json. Please define it for Vite or use the correct script."
        Pop-Location
        exit 1
    }
}
Pop-Location

# --- 6. Open frontend in default browser (Vite default port: 5173) ---
Start-Sleep -Seconds 5 # Wait for servers to spin up

$vitePort = 5173
$viteUrl = "http://localhost:$vitePort"
Write-Host "`n🌍 Opening frontend in default browser at $viteUrl..."
Start-Process $viteUrl

Write-Host "`n✅ Both servers launched. Modify code, save, and enjoy hot reload!"

exit 0
