@echo off
REM Launch Sofia in Console Mode

echo.
echo ============================================================
echo    SOFIA - Voice AI Assistant
echo    Starting Console Mode...
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

echo Starting Sofia in console mode...
echo.
echo Speak into your microphone when prompted.
echo Say "goodbye" to end the conversation.
echo.
echo Press Ctrl+C to stop Sofia
echo.

python agent-windows.py console

pause