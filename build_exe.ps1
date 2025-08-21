<#!
.SYNOPSIS
  Build a single-file Windows .exe launcher for MauEyeCare using PyInstaller.
#>
param(
  [string]$OutputName = 'MauEyeCareLauncher'
)

$ErrorActionPreference = 'Stop'

if (!(Test-Path .\.venv\Scripts\python.exe)) {
  Write-Error ".venv not found. Run setup.ps1 first."; exit 1
}

Write-Host "[MauEyeCare] Installing PyInstaller..." -ForegroundColor Yellow
& .\.venv\Scripts\pip.exe install --upgrade pyinstaller | Out-Null

Write-Host "[MauEyeCare] Building $OutputName.exe ..." -ForegroundColor Yellow
& .\.venv\Scripts\pyinstaller.exe `
  --name $OutputName `
  --onefile `
  --windowed `
  --clean `
  launcher.py

$exePath = Join-Path (Resolve-Path .\dist) ("$OutputName.exe")
if (Test-Path $exePath) {
  Write-Host "[MauEyeCare] Build complete: $exePath" -ForegroundColor Green
  Write-Host "Place the .exe in the project root next to run.ps1 for one-click startup." -ForegroundColor Cyan
} else {
  Write-Error "Build failed. Check the PyInstaller output for details."
}
