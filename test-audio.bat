@echo off
REM Test audio system

echo.
echo ============================================================
echo    SOFIA - Audio System Test
echo ============================================================
echo.

if not exist venv (
    echo [ERROR] Please run setup-windows.bat first
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

echo Testing audio capture and playback...
echo.

python -c "from src.audio.capture import AudioCapture; from src.audio.playback import AudioPlayback; import numpy as np; print('Testing 440Hz tone...'); p = AudioPlayback(16000); tone = np.sin(2*np.pi*440*np.linspace(0,1,16000)).astype(np.float32); p.play(tone); print('If you heard a beep, audio works!')"

echo.
pause