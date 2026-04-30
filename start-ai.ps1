#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Start the MauEyeCare Python AI Microservice.
    Requires Python 3.11+ and pip install -r requirements.txt
    Optionally installs Tesseract OCR if not found.
#>

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$aiDir = Join-Path $root "MauEyeCare.AI"

Write-Host "══════════════════════════════════════════" -ForegroundColor Magenta
Write-Host "  MauEyeCare AI Microservice Startup" -ForegroundColor Magenta
Write-Host "══════════════════════════════════════════" -ForegroundColor Magenta

# Check Python
try {
    $pyVer = & python --version 2>&1
    Write-Host "  Python: $pyVer" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found. Please install Python 3.11+" -ForegroundColor Red
    Write-Host "    https://www.python.org/downloads/" -ForegroundColor Gray
    exit 1
}

# Install requirements
Write-Host "`n[1/2] Installing Python dependencies..." -ForegroundColor Green
& pip install -r (Join-Path $aiDir "requirements.txt") --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "  ✗ pip install failed" -ForegroundColor Red; exit 1
}
Write-Host "  ✔ Dependencies ready" -ForegroundColor Green

# Check Tesseract
$tessPath = Get-Command "tesseract" -ErrorAction SilentlyContinue
if ($null -eq $tessPath) {
    Write-Host "`n  ⚠ Tesseract OCR not found." -ForegroundColor Yellow
    Write-Host "    Install from: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Gray
    Write-Host "    OCR endpoint will be limited without Tesseract." -ForegroundColor Gray
}

# Start Flask
Write-Host "`n[2/2] Starting AI service on http://localhost:5050..." -ForegroundColor Green
Set-Location $aiDir
& python app.py
