@echo off
title CLOUD-M7 High-Speed Node.js Forensic Dashboard
echo ==============================================================================
echo   CLOUD-M7: Launching Fast Node.js Forensic Provenance Dashboard
echo   Powered by Express, Vis-Network (WebGL/Canvas), Tailwind CSS, DuckDB & Python
echo ==============================================================================
echo.
cd /d "%~dp0web_dashboard"
start "" http://localhost:3001
node server.js
pause
