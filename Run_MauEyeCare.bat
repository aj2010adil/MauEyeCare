@echo off
TITLE MauEyeCare - Eye Care Hospital Management System
COLOR 0A

echo =========================================================================
echo                 MauEyeCare Hospital Management System
echo =========================================================================
echo.
echo [1/4] Checking Python environment...

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    where py >nul 2>nul
    if %errorlevel% neq 0 (
        COLOR 0C
        echo.
        echo [ERROR] Python is not installed or not added to PATH!
        echo Please download and install Python 3.10 or higher from:
        echo https://www.python.org/downloads/
        echo ** IMPORTANT ** Make sure to check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo [+] Python found!

echo.
echo [2/4] Setting up isolated Python virtual environment...
if not exist ".venv" (
    echo [*] Creating virtual environment .venv...
    %PYTHON_CMD% -m venv .venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

echo.
echo [3/4] Checking required packages...
if not exist ".venv\.installed" (
    echo [*] Installing required Python packages - first run only
    python -m pip install --quiet --upgrade pip
    python -m pip install --quiet -r requirements.txt
    if %errorlevel% equ 0 (
        echo installed > ".venv\.installed"
    )
) else (
    echo [+] Dependencies already installed.
)

REM Ensure streamlit config exists
if not exist ".streamlit" mkdir .streamlit
if not exist ".streamlit\credentials.toml" (
    (
        echo [general]
        echo email = ""
    ) > .streamlit\credentials.toml
)
if not exist ".streamlit\config.toml" (
    (
        echo [server]
        echo headless = true
        echo port = 8501
        echo enableCORS = false
        echo enableXsrfProtection = false
        echo.
        echo [browser]
        echo gatherUsageStats = false
        echo.
        echo [theme]
        echo primaryColor = "#1E3A8A"
        echo backgroundColor = "#FFFFFF"
        echo secondaryBackgroundColor = "#F8FAFC"
        echo textColor = "#0F172A"
    ) > .streamlit\config.toml
)

echo.
echo [4/4] Starting MauEyeCare Streamlit Application...
echo.
echo =========================================================================
echo  APP IS RUNNING! 
echo  Opening browser at: http://localhost:8501
echo  KEEP THIS WINDOW OPEN WHILE WORKING IN MAUEYECARE.
echo  To close the app, simply close this window.
echo =========================================================================
echo.

REM Automatically open browser in default web browser
start http://localhost:8501

python -m streamlit run main_app_streamlined.py

pause
