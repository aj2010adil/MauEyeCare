$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$apiDir = Join-Path $root "MauEyeCare.API"
$desktopDir = Join-Path $root "MauEyeCare.Desktop"
$aiDir = Join-Path $root "MauEyeCare.AI"
$mcpDir = Join-Path $root "MauEyeCare.MCP"

Write-Host "=========================================="
Write-Host "  MauEyeCare Suite Bootstrapper v1.2.0"
Write-Host "=========================================="

Write-Host "Cleaning up existing processes..."
Stop-Process -Name "dotnet", "python", "MauEyeCare.Desktop", "MauEyeCare.API" -Force -ErrorAction SilentlyContinue

Write-Host "Building components..."
dotnet build "$root\MauEyeCare.sln"

Write-Host "Launching background services..."
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "python app.py" -WorkingDirectory $aiDir
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "dotnet run" -WorkingDirectory $apiDir
Start-Process "powershell" -ArgumentList "-NoExit", "-Command", "dotnet run" -WorkingDirectory $mcpDir

Write-Host "Launching Desktop App..."
$desktopExe = Join-Path $desktopDir "bin\Debug\net8.0-windows\MauEyeCare.Desktop.exe"
if (Test-Path $desktopExe) {
    Start-Process $desktopExe -WorkingDirectory $root
} else {
    dotnet run --project "$desktopDir\MauEyeCare.Desktop.csproj" --no-build
}

Write-Host "✔ Done! Check the separate windows for service logs."
