#!/usr/bin/env pwsh
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiDir = Join-Path $root "MauEyeCare.API"
$desktopDir = Join-Path $root "MauEyeCare.Desktop"
$aiDir = Join-Path $root "MauEyeCare.AI"
$mcpDir = Join-Path $root "MauEyeCare.MCP"

Write-Host "══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  MauEyeCare — Robust Bootstrapper" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════" -ForegroundColor Cyan

# 0. Kill existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Stop-Process -Name "dotnet", "python", "MauEyeCare.Desktop", "MauEyeCare.API" -Force -ErrorAction SilentlyContinue

# 1. Build everything
Write-Host "`n[1/4] Building API..." -ForegroundColor Green
dotnet build "$apiDir\MauEyeCare.API.csproj"

Write-Host "`n[2/4] Building Desktop..." -ForegroundColor Green
dotnet build "$desktopDir\MauEyeCare.Desktop.csproj"

Write-Host "`n[3/4] Building MCP Server..." -ForegroundColor Green
dotnet build "$mcpDir\MauEyeCare.MCP.csproj"

Write-Host "`n[4/4] Building AI dependencies..." -ForegroundColor Green
# (Assume python is in path and requirements are met)

# 2. Start AI in a new window
Write-Host "`nLaunching AI Service..." -ForegroundColor Green
$aiCmd = "cd `"$aiDir`" ; python app.py"
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "$aiCmd"

# 3. Start API in a new window
Write-Host "Launching API Backend..." -ForegroundColor Green
$apiCmd = "cd `"$root`" ; dotnet run --project `"$apiDir\MauEyeCare.API.csproj`""
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "$apiCmd"

# 4. Start MCP Server in a new window (Optional, for developer use)
Write-Host "Launching MCP Server..." -ForegroundColor Green
$mcpCmd = "cd `"$mcpDir`" ; dotnet run"
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "$mcpCmd"

# 5. Start Desktop App
Write-Host "Launching WPF Frontend..." -ForegroundColor Green
$desktopExe = Join-Path $desktopDir "bin\Debug\net8.0-windows\MauEyeCare.Desktop.exe"
if (Test-Path $desktopExe) {
    Start-Process $desktopExe -WorkingDirectory $root
} else {
    Write-Host "Desktop EXE not found, using dotnet run..." -ForegroundColor Yellow
    dotnet run --project "$desktopDir\MauEyeCare.Desktop.csproj" --no-build
}

Write-Host "`n✔ MauEyeCare Suite is starting!" -ForegroundColor Green
Write-Host "Check the newly opened terminal windows for logs." -ForegroundColor White
