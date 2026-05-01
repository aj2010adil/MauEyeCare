# Explicit Bootstrapper
$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot

Write-Host 'Cleaning up...'
Stop-Process -Name 'dotnet' -Force -ErrorAction SilentlyContinue
Stop-Process -Name 'python' -Force -ErrorAction SilentlyContinue

Write-Host 'Building Solution...'
dotnet build "$root\MauEyeCare.sln"

Write-Host 'Launching AI...'
Start-Process 'powershell.exe' -ArgumentList '-NoExit', '-Command', 'python app.py' -WorkingDirectory "$root\MauEyeCare.AI"

Write-Host 'Launching API...'
Start-Process 'powershell.exe' -ArgumentList '-NoExit', '-Command', 'dotnet run --project MauEyeCare.API.csproj' -WorkingDirectory "$root\MauEyeCare.API"

Write-Host 'Launching MCP...'
Start-Process 'powershell.exe' -ArgumentList '-NoExit', '-Command', 'dotnet run --project MauEyeCare.MCP.csproj' -WorkingDirectory "$root\MauEyeCare.MCP"

Write-Host 'Launching Desktop Frontend...'
Start-Process 'powershell.exe' -ArgumentList '-NoExit', '-Command', 'dotnet run --project MauEyeCare.Desktop.csproj --no-build' -WorkingDirectory "$root\MauEyeCare.Desktop"

Write-Host 'DONE'
