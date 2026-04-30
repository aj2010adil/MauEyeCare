#!/usr/bin/env pwsh
<#
.SYNOPSIS
    MauEyeCare — Rebuild and Run Suite
    Cleans, builds, and starts all dependencies (API, Desktop, AI Microservice).
#>

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiDir = Join-Path $root "MauEyeCare.API"
$desktopDir = Join-Path $root "MauEyeCare.Desktop"
$aiDir = Join-Path $root "MauEyeCare.AI"

Write-Host "══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  MauEyeCare — Clean and Build Protocol" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════" -ForegroundColor Cyan

# 1. Rebuild API
Write-Host "`n[1/3] Building API..." -ForegroundColor Green
dotnet clean "$apiDir\MauEyeCare.API.csproj"
dotnet build "$apiDir\MauEyeCare.API.csproj"

# 2. Rebuild Desktop
Write-Host "`n[2/3] Building Desktop App..." -ForegroundColor Green
dotnet clean "$desktopDir\MauEyeCare.Desktop.csproj"
dotnet build "$desktopDir\MauEyeCare.Desktop.csproj"

# 3. Start AI Microservice
Write-Host "`n[3/3] Launching AI and Continuous Learning Pipelines..." -ForegroundColor Green
if (Test-Path "$aiDir\venv") {
    Start-Process "$aiDir\venv\Scripts\python.exe" -ArgumentList "$aiDir\app.py" -WorkingDirectory $aiDir -NoNewWindow
} else {
    Start-Process "python" -ArgumentList "$aiDir\app.py" -WorkingDirectory $aiDir -NoNewWindow
}

# 4. Run API in background
Write-Host "`nStarting API Backend..." -ForegroundColor Green
$apiProc = Start-Process "dotnet" -ArgumentList "run --project `"$apiDir\MauEyeCare.API.csproj`"" -WorkingDirectory $root -PassThru -NoNewWindow

# 5. Run Desktop
Write-Host "`nLaunching WPF Frontend..." -ForegroundColor Green
Start-Process "dotnet" -ArgumentList "run --project `"$desktopDir\MauEyeCare.Desktop.csproj`"" -WorkingDirectory $root

Write-Host "`n✔ MauEyeCare Clinical Suite Bootstrapped!" -ForegroundColor Green
