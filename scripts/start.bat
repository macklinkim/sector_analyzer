@echo off
echo [Economi Analyzer] Starting server...
cd /d "%~dp0..\backend"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Python venv not found. Run: cd backend ^&^& python -m venv .venv ^&^& .venv\Scripts\pip install -e ".[dev]"
    pause
    exit /b 1
)

echo [OK] Backend: http://localhost:8000
echo [OK] Swagger: http://localhost:8000/docs
echo [OK] Press Ctrl+C to stop
echo.
.venv\Scripts\python.exe -m uvicorn app.main:app --port 8000
