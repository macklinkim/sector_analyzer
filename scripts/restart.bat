@echo off
echo [Economi Analyzer] Restarting...
echo.

echo [1/4] Stopping server...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Building frontend...
cd /d "%~dp0..\frontend"
call npm run build
if %errorlevel% neq 0 (
    echo [ERROR] Frontend build failed.
    pause
    exit /b 1
)

echo [3/4] Running backend tests...
cd /d "%~dp0..\backend"
.venv\Scripts\python.exe -m pytest -q
if %errorlevel% neq 0 (
    echo [WARN] Some tests failed. Starting server anyway...
)

echo [4/4] Starting server...
echo.
echo [OK] Backend: http://localhost:8000
echo [OK] Press Ctrl+C to stop
echo.
.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
