@echo off
setlocal enabledelayedexpansion

:: Create logs folder if missing
if not exist logs (
    mkdir logs
)

:: Start backend
echo Starting FastAPI backend...
start "" cmd /c "cd backend && uvicorn main:app --reload > ../logs/backend.log 2>&1"

:: Start frontend
echo Starting Vite frontend...
start "" cmd /c "cd frontend && npm run dev > ../logs/frontend.log 2>&1"

:: Wait briefly before opening browser
timeout /t 5 >nul

:: Open browser to localhost
start http://localhost:5173

echo MauEyeCare launched. Check logs/ for errors if needed.
pause
