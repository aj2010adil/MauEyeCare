@echo off
echo Installing MauEyeCare with UV...

REM Check if UV is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo UV not found. Installing UV...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo Failed to install UV. Please install manually from https://github.com/astral-sh/uv
        pause
        exit /b 1
    )
)

echo UV found. Installing dependencies...
uv sync

if %errorlevel% neq 0 (
    echo Failed to install dependencies with UV
    pause
    exit /b 1
)

echo Installation complete!
echo Starting MauEyeCare system...
python start_system.py

pause