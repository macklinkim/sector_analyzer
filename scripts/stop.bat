@echo off
echo [Economi Analyzer] Stopping server...
taskkill /F /IM python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Server stopped.
) else (
    echo [INFO] No running server found.
)
