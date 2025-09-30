@echo off
REM Run Sofia Test Suite

echo.
echo ============================================================
echo    SOFIA - Test Suite
echo ============================================================
echo.

if not exist venv (
    echo [ERROR] Virtual environment not found!
    echo Please run setup-windows.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Running comprehensive test suite...
echo.
echo Choose test mode:
echo   1. Automatic (no microphone/playback)
echo   2. Interactive (with microphone/playback)
echo.
set /p choice="Enter choice (1 or 2): "

if "%choice%"=="2" (
    echo.
    echo Running INTERACTIVE tests...
    python tests\run_all_tests.py --interactive
) else (
    echo.
    echo Running AUTOMATIC tests...
    python tests\run_all_tests.py
)

echo.
pause