@echo off
setlocal

cd /d "%~dp0"
set "LOG_FILE=%~dp0logs\spotify_ad_muter.log"

if not exist "%LOG_FILE%" (
    echo Log file not found: %LOG_FILE%
    echo Start the muter first so it can create the log file.
    exit /b 1
)

echo Showing live logs from: %LOG_FILE%
echo Press Ctrl+C to stop.
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-Content -Path \"%LOG_FILE%\" -Wait -Tail 40"
