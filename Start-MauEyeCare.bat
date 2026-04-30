@echo off
echo ========================================================
echo       MauEyeCare Clinical Suite - Master Launcher
echo ========================================================
echo.
echo [1/3] Cleaning up old background processes...
taskkill /F /IM MauEyeCare.Desktop.exe /T >nul 2>&1
taskkill /F /IM MauEyeCare.API.exe /T >nul 2>&1

echo.
echo [2/3] Building Production Suite...
echo Please wait, this may take a moment.
powershell -ExecutionPolicy Bypass -File .\build-production.ps1

echo.
echo [3/3] Launching MauEyeCare...
start .\Dist\MauEyeCare_ClinicalSuite\MauEyeCare.Desktop.exe

echo.
echo MauEyeCare is now running! You can close this window.
timeout /t 5 >nul
