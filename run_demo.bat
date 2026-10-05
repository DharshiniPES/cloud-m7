@echo off
cd /d "%~dp0"
echo ===================================================
echo   CLOUD-M7: Running Capstone Review 1 Live Demo
echo ===================================================
call .\.venv\Scripts\python.exe scripts\run_demo.py
echo.
pause
