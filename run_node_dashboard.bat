@echo off
title CLOUD-M7 High-Speed Node.js Forensic Dashboard
echo ==============================================================================
echo   CLOUD-M7: Launching Fast Node.js Forensic Provenance Dashboard
echo   Powered by Express, Vis-Network (WebGL/Canvas), Tailwind CSS, DuckDB & Python
echo ==============================================================================
echo.
cd /d "%~dp0web_dashboard"

echo [1/2] Checking Node.js environment...
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not found in PATH! Please install Node.js v18+.
    pause
    exit /b 1
)

echo [2/2] Starting Node.js Express server on http://localhost:3001 ...
start "" http://localhost:3001
node server.js
pause
