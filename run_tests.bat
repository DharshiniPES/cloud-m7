@echo off
cd /d "%~dp0"
echo ===================================================
echo   CLOUD-M7: Running Automated Verification Tests
echo ===================================================
call .\.venv\Scripts\pytest.exe -v
echo.
pause
