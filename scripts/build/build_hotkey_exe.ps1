# PowerShell script to build the TTS Hotkey executable for Windows

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🎤 BUILDING TTS HOTKEY EXECUTABLE" -ForegroundColor Yellow
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check if the configurable hotkey file exists
if (-not (Test-Path "tts_hotkey_configurable.py")) {
    Write-Host "❌ ERROR: tts_hotkey_configurable.py not found!" -ForegroundColor Red
    Write-Host "Make sure you are in the project root directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 ANALYZING CONFIGURATION..." -ForegroundColor Green

# Read configuration from the file
$config_content = Get-Content "tts_hotkey_configurable.py" -Raw -Encoding UTF8

# Extract main configurations
$discord_url = ""
$engine = "gtts"

if ($config_content -match 'DEFAULT_DISCORD_BOT_URL\s*=\s*"([^"]+)"') {
    $discord_url = $matches[1]
}

if ($config_content -match 'DEFAULT_TTS_ENGINE\s*=\s*"([^"]+)"') {
    $engine = $matches[1]
}

Write-Host "📊 DETECTED CONFIGURATION:" -ForegroundColor Cyan
Write-Host "   Discord Bot URL: $discord_url" -ForegroundColor White
Write-Host "   TTS Engine: $engine" -ForegroundColor White
Write-Host ""

# Install dependencies
Write-Host "📦 INSTALLING DEPENDENCIES..." -ForegroundColor Green

if (Test-Path "requirements.txt") {
    Write-Host "Installing from requirements.txt..." -ForegroundColor Yellow
    try {
        & python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
        Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ ERROR installing dependencies!" -ForegroundColor Red
        Write-Host "Check if Python is available and try manually:" -ForegroundColor Yellow
        Write-Host "   python -m pip install -r requirements.txt" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "⚠️ requirements.txt not found - installing essential packages..." -ForegroundColor Yellow
    & python -m pip install pyinstaller requests keyboard pyttsx3 gtts pygame sounddevice pystray pillow python-dotenv
}

# Check/Install PyInstaller
Write-Host "🔧 CHECKING PYINSTALLER..." -ForegroundColor Green
try {
    $pyinstaller_version = & python -m PyInstaller --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PyInstaller found: $pyinstaller_version" -ForegroundColor Green
    } else {
        throw "PyInstaller not working"
    }
} catch {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    try {
        & python -m pip install pyinstaller
        Write-Host "✅ PyInstaller installed!" -ForegroundColor Green
    } catch {
        Write-Host "❌ ERROR installing PyInstaller!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🔨 BUILDING EXECUTABLE..." -ForegroundColor Green
Write-Host "This may take a few minutes..." -ForegroundColor Yellow
Write-Host ""

# Build command with all necessary hidden imports
$buildArgs = @(
    "--onefile",
    "--console",
    "--name=tts_hotkey",
    # Core dependencies
    "--hidden-import=requests",
    "--hidden-import=urllib3",
    "--hidden-import=certifi",
    "--hidden-import=json",
    "--hidden-import=threading",
    "--hidden-import=time",
    "--hidden-import=os",
    "--hidden-import=sys",
    # Keyboard handling
    "--hidden-import=keyboard",
    # TTS engines
    "--hidden-import=pyttsx3",
    "--hidden-import=gtts",
    "--hidden-import=io",
    # Audio playback
    "--hidden-import=pygame",
    "--hidden-import=pygame.mixer",
    "--hidden-import=sounddevice",
    "--hidden-import=soundfile",
    "--hidden-import=numpy",
    # System tray
    "--hidden-import=pystray",
    "--hidden-import=PIL",
    "--hidden-import=PIL.Image",
    # Environment
    "--hidden-import=python_dotenv",
    # Windows specific
    "--hidden-import=win32api",
    "--hidden-import=win32con",
    "--hidden-import=win32gui",
    # Configuration file
    "tts_hotkey_configurable.py"
)

# Add icon if available
if (Test-Path "icon.ico") {
    $buildArgs = @("--icon=icon.ico") + $buildArgs
    Write-Host "✅ Using icon: icon.ico" -ForegroundColor Green
} elseif (Test-Path "icon.png") {
    Write-Host "⚠️ Found icon.png but need icon.ico for Windows executable" -ForegroundColor Yellow
} else {
    Write-Host "⚠️ No icon found - building without custom icon" -ForegroundColor Yellow
}

# Execute PyInstaller
try {
    & python -m PyInstaller @buildArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host "✅ EXECUTABLE BUILT SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host ""
        
        if (Test-Path "dist/tts_hotkey.exe") {
            $exeSize = (Get-Item "dist/tts_hotkey.exe").Length
            $exeSizeMB = [math]::Round($exeSize / 1MB, 2)
            
            Write-Host "📁 Location: dist/tts_hotkey.exe" -ForegroundColor Cyan
            Write-Host "📏 Size: $exeSizeMB MB" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "🎯 FEATURES:" -ForegroundColor Yellow
            Write-Host "   ✅ Standalone executable (no Python required)" -ForegroundColor White
            Write-Host "   ✅ Built-in TTS configuration" -ForegroundColor White
            Write-Host "   ✅ Discord bot integration" -ForegroundColor White
            Write-Host "   ✅ Hotkey support" -ForegroundColor White
            Write-Host ""
            Write-Host "🚀 TO USE:" -ForegroundColor Yellow
            Write-Host "   1. Copy dist/tts_hotkey.exe to desired location" -ForegroundColor White
            Write-Host "   2. Run the executable" -ForegroundColor White
            Write-Host "   3. Use configured hotkeys to trigger TTS" -ForegroundColor White
            Write-Host ""
            
            # Create a simple batch file for easy execution
            $batContent = @"
@echo off
title TTS Hotkey Application
echo.
echo =======================================
echo   TTS HOTKEY - Starting Application
echo =======================================
echo.
echo Discord Bot URL: $discord_url
echo TTS Engine: $engine
echo.
echo Press any key to start...
pause >nul
echo.
echo Starting TTS Hotkey application...
echo Press Ctrl+C to stop
echo.
dist\tts_hotkey.exe
echo.
echo Application closed. Press any key to exit...
pause >nul
"@
            Set-Content -Path "run_tts_hotkey.bat" -Value $batContent -Encoding ASCII
            Write-Host "📝 Created run_tts_hotkey.bat for easy execution" -ForegroundColor Green
            Write-Host ""
            
        } else {
            Write-Host "❌ Executable not found in dist/ directory!" -ForegroundColor Red
            exit 1
        }
        
    } else {
        throw "PyInstaller failed"
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ BUILD FAILED!" -ForegroundColor Red
    Write-Host "Check the error messages above for details" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 TROUBLESHOOTING:" -ForegroundColor Yellow
    Write-Host "   1. Make sure Python and pip are working" -ForegroundColor White
    Write-Host "   2. Check if all dependencies are installed" -ForegroundColor White
    Write-Host "   3. Try running: python tts_hotkey_configurable.py first" -ForegroundColor White
    Write-Host ""
    exit 1
}

Write-Host "🎉 BUILD PROCESS COMPLETED!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the executable: run_tts_hotkey.bat" -ForegroundColor White
Write-Host "2. If it works, distribute: dist/tts_hotkey.exe" -ForegroundColor White
Write-Host "3. Share the batch file for easy user experience" -ForegroundColor White
Write-Host ""