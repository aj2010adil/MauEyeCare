# Minimalist Bootstrapper
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Host 'Cleaning up...'
Stop-Process -Name 'dotnet' -Force -ErrorAction SilentlyContinue
Stop-Process -Name 'python' -Force -ErrorAction SilentlyContinue

Write-Host 'Building...'
dotnet build "$root\MauEyeCare.sln"

Write-Host 'Launching AI...'
Start-Process 'powershell.exe' -ArgumentList '-NoExit', '-Command', 'python app.py' -WorkingDirectory "$root\MauEyeCare.AI"

Write-Host 'Launching API...'
Start-Process 'powershell.exe' -ArgumentList '-NoExit', '-Command', 'dotnet run' -WorkingDirectory "$root\MauEyeCare.API"

Write-Host 'Launching MCP...'
Start-Process 'powershell.exe' -ArgumentList '-NoExit', '-Command', 'dotnet run' -WorkingDirectory "$root\MauEyeCare.MCP"

Write-Host 'Launching Desktop...'
Start-Process 'powershell.exe' -ArgumentList '-NoExit', '-Command', 'dotnet run --no-build' -WorkingDirectory "$root\MauEyeCare.Desktop"

Write-Host 'DONE'
