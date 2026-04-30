#!/usr/bin/env pwsh
<#
.SYNOPSIS
    MauEyeCare — One-shot startup script
    Starts the API backend, then the WPF desktop app.
    The Python AI microservice must be started separately (see start-ai.ps1).

.USAGE
    .\start-dev.ps1
#>

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiDir = Join-Path $root "MauEyeCare.API"
$desktopDir = Join-Path $root "MauEyeCare.Desktop"

Write-Host "══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  MauEyeCare — Development Startup" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════" -ForegroundColor Cyan

# 1. Start API in background
Write-Host "`n[1/2] Starting ASP.NET Core API..." -ForegroundColor Green
$apiProc = Start-Process "dotnet" -ArgumentList "run --project `"$apiDir`"" `
    -WorkingDirectory $root -PassThru -NoNewWindow
Write-Host "  API PID: $($apiProc.Id) — https://localhost:5001" -ForegroundColor Gray
Write-Host "  Swagger: https://localhost:5001/swagger" -ForegroundColor Gray

# Wait for API to be ready
Write-Host "  Waiting for API to start..." -ForegroundColor Yellow
$maxAttempts = 20; $attempt = 0; $apiReady = $false
while ($attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    try {
        $resp = Invoke-WebRequest -Uri "https://localhost:5001/api/v1/auth/login" `
            -Method POST -SkipCertificateCheck -ErrorAction SilentlyContinue
        $apiReady = $true; break
    } catch { $attempt++ }
}

if ($apiReady) {
    Write-Host "  ✔ API is ready!" -ForegroundColor Green
} else {
    Write-Host "  ⚠ API may not be fully ready. Proceeding..." -ForegroundColor Yellow
}

# 2. Start Desktop App
Write-Host "`n[2/2] Starting WPF Desktop App..." -ForegroundColor Green
Start-Process "dotnet" -ArgumentList "run --project `"$desktopDir`"" `
    -WorkingDirectory $root

Write-Host "`n✔ MauEyeCare is running!" -ForegroundColor Green
Write-Host "  • API:     https://localhost:5001" -ForegroundColor Gray
Write-Host "  • Swagger: https://localhost:5001/swagger" -ForegroundColor Gray
Write-Host "  • AI:      http://localhost:5050 (start separately with start-ai.ps1)" -ForegroundColor Gray
Write-Host "`nPress Ctrl+C to stop..." -ForegroundColor Gray
$apiProc.WaitForExit()
