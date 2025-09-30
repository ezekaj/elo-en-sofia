@echo off
REM Sofia Windows Setup Script
REM Installs Sofia with Windows-native optimizations

echo.
echo ============================================================
echo    SOFIA WINDOWS SETUP
echo    100%% Local Voice AI Assistant
echo ============================================================
echo.

REM Check Python installation
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.10 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

python --version
echo [OK] Python found
echo.

REM Check Ollama installation
echo [2/6] Checking Ollama installation...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not installed or not in PATH
    echo.
    echo Please install Ollama from:
    echo https://ollama.com/download
    echo.
    pause
    exit /b 1
)

ollama --version
echo [OK] Ollama found
echo.

REM Check if Ollama is running
echo [3/6] Checking if Ollama is running...
ollama list >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Ollama is not running
    echo Starting Ollama in background...
    start /B ollama serve
    timeout /t 3 >nul
)

echo [OK] Ollama is running
echo.

REM Check for gemma3:4b model
echo [4/6] Checking for gemma3:4b model...
ollama list | findstr "gemma3:4b" >nul
if errorlevel 1 (
    echo [INFO] Model gemma3:4b not found. Pulling...
    echo This will download ~3.3GB, please be patient...
    ollama pull gemma3:4b
    if errorlevel 1 (
        echo [ERROR] Failed to pull model
        pause
        exit /b 1
    )
)

echo [OK] Model gemma3:4b ready
echo.

REM Create virtual environment
echo [5/6] Creating Python virtual environment...
if exist venv (
    echo [INFO] Virtual environment already exists, skipping
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created
)
echo.

REM Install dependencies
echo [6/6] Installing Windows-optimized dependencies...
echo This will take 2-3 minutes...
echo.

call venv\Scripts\activate.bat
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements-windows.txt

if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies
    echo.
    echo Try running this command manually:
    echo   venv\Scripts\pip install -r requirements-windows.txt
    echo.
    pause
    exit /b 1
)

echo.
echo [OK] All dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file...
    copy .env.example .env >nul 2>&1
)

REM Success message
echo ============================================================
echo    SETUP COMPLETE!
echo ============================================================
echo.
echo Sofia is ready to use. You can now run:
echo.
echo   1. run-gradio.bat   - Web interface (recommended)
echo   2. run-console.bat  - Terminal interface
echo.
echo For first-time users, we recommend the web interface.
echo.
echo The first run will download AI models (~100MB for Whisper).
echo.
pause