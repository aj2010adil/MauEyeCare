Write-Host "Starting MauEyeCare AI Service..." -ForegroundColor Cyan
Start-Process python -ArgumentList "app.py" -WorkingDirectory "d:\MauEyeCare\MauEyeCare\MauEyeCare.AI" -WindowStyle Minimized

Write-Host "Starting MauEyeCare API..." -ForegroundColor Cyan
Start-Process dotnet -ArgumentList "run" -WorkingDirectory "d:\MauEyeCare\MauEyeCare\MauEyeCare.API" -WindowStyle Minimized

Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Launching MauEyeCare Desktop App..." -ForegroundColor Green
Start-Process dotnet -ArgumentList "run" -WorkingDirectory "d:\MauEyeCare\MauEyeCare\MauEyeCare.Desktop"
