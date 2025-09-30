@echo off
REM Launch Sofia with Gradio Web Interface

echo.
echo ============================================================
echo    SOFIA - Voice AI Assistant
echo    Starting Web Interface...
echo ============================================================
echo.

REM Check if venv exists
if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please run setup-windows.bat first
    echo.
    pause
    exit /b 1
)

REM Activate venv and run
call venv\Scripts\activate.bat

echo Starting Sofia...
echo.
echo The web interface will open in your browser automatically.
echo If not, navigate to: http://localhost:7860
echo.
echo Press Ctrl+C to stop Sofia
echo.

python agent-windows.py gradio

pause