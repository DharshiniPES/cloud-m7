@echo off
REM CLOUD-M7 PowerPoint Presentation Generator
echo ======================================================================
echo   CLOUD-M7: Generating Review 1 PowerPoint Presentation Deck (.pptx)
echo ======================================================================

cd /d "%~dp0"
.\.venv\Scripts\python.exe scripts\generate_presentation.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Presentation generation failed.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [+] Presentation successfully generated!
echo [+] File Location: reports\CLOUD-M7_Review1_Final_Presentation.pptx
echo.
pause
