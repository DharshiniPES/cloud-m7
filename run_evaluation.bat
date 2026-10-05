@echo off
cd /d "%~dp0"
echo ===================================================
echo   CLOUD-M7: Running Benchmark & Feature Comparison
echo ===================================================
call .\.venv\Scripts\python.exe scripts\generate_evaluation.py
echo.
pause
