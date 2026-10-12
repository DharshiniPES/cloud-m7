@echo off
REM CLOUD-M7 Technical Word Summary Generator
echo ======================================================================
echo   CLOUD-M7: Generating Comprehensive Project Summary Document (.docx)
echo ======================================================================

cd /d "%~dp0"
.\.venv\Scripts\python.exe scripts\generate_summary_document.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Document generation failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [+] Word Document successfully generated!
echo [+] File Location: reports\CLOUD-M7_Comprehensive_Project_Summary.docx
echo.
pause
