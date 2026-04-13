@echo off
REM ----------------------------------------------------------------
REM 분할 트리거 스크립트 (Windows)
REM Usage: trigger-split.bat [base_url] [api_key]
REM ----------------------------------------------------------------

setlocal enabledelayedexpansion

set BASE_URL=%1
if "%BASE_URL%"=="" set BASE_URL=https://sector-analyzer.onrender.com
set API_KEY=%2
if "%API_KEY%"=="" set API_KEY=economi-trigger-2026
set API_BASE=%BASE_URL%/api/analysis

echo [%TIME%] Step 1/4: Waking up server...
curl -s -o NUL --max-time 90 "%BASE_URL%/health"
echo [%TIME%] Server is awake.

echo [%TIME%] Step 2/4: Triggering data + news in parallel...
start /b cmd /c "curl -s --max-time 180 -X POST "%API_BASE%/trigger/data" -H "X-API-Key: %API_KEY%" -H "Content-Type: application/json" -o %TEMP%\trigger_data.json 2>NUL && echo DATA_DONE > %TEMP%\trigger_data.flag"
start /b cmd /c "curl -s --max-time 180 -X POST "%API_BASE%/trigger/news" -H "X-API-Key: %API_KEY%" -H "Content-Type: application/json" -o %TEMP%\trigger_news.json 2>NUL && echo NEWS_DONE > %TEMP%\trigger_news.flag"

echo [%TIME%] Step 3/4: Waiting for data + news...
:WAIT_LOOP
if exist "%TEMP%\trigger_data.flag" if exist "%TEMP%\trigger_news.flag" goto WAIT_DONE
timeout /t 5 /nobreak >NUL
goto WAIT_LOOP

:WAIT_DONE
del "%TEMP%\trigger_data.flag" 2>NUL
del "%TEMP%\trigger_news.flag" 2>NUL
echo [%TIME%] Data + News completed.

echo [%TIME%] Step 4/4: Triggering AI analysis...
curl -s --max-time 300 -X POST "%API_BASE%/trigger/analyze" -H "X-API-Key: %API_KEY%" -H "Content-Type: application/json"
echo.
echo [%TIME%] Done.

del "%TEMP%\trigger_data.json" 2>NUL
del "%TEMP%\trigger_news.json" 2>NUL
endlocal
