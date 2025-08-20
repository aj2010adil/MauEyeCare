<#
.SYNOPSIS
    Starts the MauEyeCare backend API and the Streamlit Prescription Writer app.
#>

Write-Host "[MauEyeCare] Starting services for Prescription Writer..." -ForegroundColor Cyan
$ErrorActionPreference = 'Stop'

if (!(Test-Path .venv)) { Write-Error ".venv not found. Run setup.ps1 first."; exit 1 }

# Start the backend API in the background on port 8001
Write-Host "Starting backend API on port 8001..."
Start-Job -Name "backend" -ScriptBlock { 
    & .\.venv\Scripts\uvicorn main:app --host 127.0.0.1 --port 8001 
} | Out-Null

Start-Sleep -Seconds 3 # Give the backend a moment to start

# Start the Streamlit app in the foreground
try {
    Write-Host "Starting Streamlit Prescription Writer... Access it in your browser."
    & .\.venv\Scripts\streamlit run prescription_app.py
} finally {
    Write-Host "Shutting down background API job..." -ForegroundColor Yellow
    Get-Job -Name "backend" | Stop-Job -ErrorAction SilentlyContinue | Out-Null
    Get-Job -Name "backend" | Remove-Job -ErrorAction SilentlyContinue | Out-Null
    Write-Host "Cleanup complete."
}