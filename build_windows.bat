@echo off
REM Batch script to build TTS Hotkey executable on Windows
REM Alternative for systems without PowerShell

title Building TTS Hotkey Executable

echo.
echo =======================================
echo   TTS HOTKEY - WINDOWS BUILD SCRIPT
echo =======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python and make sure it's in your PATH
    pause
    exit /b 1
)

echo Python found: 
python --version

REM Check if main file exists
if not exist "tts_hotkey_configurable.py" (
    echo ERROR: tts_hotkey_configurable.py not found!
    echo Make sure you are in the correct directory
    pause
    exit /b 1
)

echo Found: tts_hotkey_configurable.py

REM Install dependencies
echo.
echo Installing dependencies...
echo.

if exist "requirements.txt" (
    echo Installing from requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install requirements
        pause
        exit /b 1
    )
) else (
    echo Installing essential packages...
    python -m pip install pyinstaller requests keyboard pyttsx3 gtts pygame sounddevice pystray pillow python-dotenv
)

REM Check PyInstaller
echo.
echo Checking PyInstaller...
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo PyInstaller ready!

REM Build the executable
echo.
echo Building executable...
echo This may take a few minutes...
echo.

python -m PyInstaller ^
    --onefile ^
    --console ^
    --name=tts_hotkey ^
    --hidden-import=requests ^
    --hidden-import=urllib3 ^
    --hidden-import=certifi ^
    --hidden-import=keyboard ^
    --hidden-import=pyttsx3 ^
    --hidden-import=gtts ^
    --hidden-import=pygame ^
    --hidden-import=pygame.mixer ^
    --hidden-import=sounddevice ^
    --hidden-import=pystray ^
    --hidden-import=PIL ^
    --hidden-import=PIL.Image ^
    --hidden-import=python_dotenv ^
    tts_hotkey_configurable.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo Check the error messages above
    pause
    exit /b 1
)

REM Check if executable was created
if not exist "dist\tts_hotkey.exe" (
    echo.
    echo ERROR: Executable not found in dist directory!
    pause
    exit /b 1
)

REM Success!
echo.
echo =======================================
echo   BUILD SUCCESSFUL!
echo =======================================
echo.
echo Executable created: dist\tts_hotkey.exe
echo.

REM Get file size
for %%A in ("dist\tts_hotkey.exe") do (
    set size=%%~zA
    set /a sizeMB=!size!/1024/1024
)

echo File size: %sizeMB% MB (approx)
echo.
echo FEATURES:
echo   - Standalone executable (no Python required)
echo   - Built-in TTS configuration  
echo   - Discord bot integration
echo   - Hotkey support
echo   - System tray integration
echo.

REM Create run batch file
echo Creating run_tts_hotkey.bat...
(
    echo @echo off
    echo title TTS Hotkey Application
    echo echo.
    echo echo =======================================
    echo echo   TTS HOTKEY - Starting Application
    echo echo =======================================
    echo echo.
    echo echo Press any key to start...
    echo pause ^>nul
    echo echo.
    echo echo Starting TTS Hotkey application...
    echo echo Press Ctrl+C to stop
    echo echo.
    echo dist\tts_hotkey.exe
    echo echo.
    echo echo Application closed. Press any key to exit...
    echo pause ^>nul
) > run_tts_hotkey.bat

echo Created: run_tts_hotkey.bat
echo.
echo TO USE:
echo   1. Run: run_tts_hotkey.bat
echo   2. Or directly: dist\tts_hotkey.exe  
echo   3. Use configured hotkeys for TTS
echo.
echo BUILD COMPLETED!
echo.
pause