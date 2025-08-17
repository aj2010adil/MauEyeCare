@echo off
echo ============================================================
echo MauEyeCare - AI Eye Care System
echo ============================================================
echo.

cd /d "%~dp0"

echo Installing dependencies...
pip install streamlit pandas fpdf2 requests python-docx opencv-python-headless Pillow numpy beautifulsoup4

echo.
echo Starting MauEyeCare Application...
echo Access the app at: http://localhost:8507
echo Press Ctrl+C to stop the application
echo.

python -m streamlit run main_app.py --server.port 8507

pause