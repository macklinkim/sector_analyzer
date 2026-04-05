@echo off
echo [Economi Analyzer] Triggering AI pipeline...
echo.

set /p APIKEY="Enter TRIGGER_API_KEY (default: economi-trigger-2026): "
if "%APIKEY%"=="" set APIKEY=economi-trigger-2026

curl -s -X POST http://localhost:8000/api/analysis/trigger -H "X-API-Key: %APIKEY%" -H "Content-Type: application/json"
echo.
echo.
echo [OK] Pipeline triggered. Check http://localhost:8000 for results.
pause
