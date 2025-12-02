# Build Script for Simple TTS Hotkey (Minimal Dependencies)
# This version only requires: requests and keyboard

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🎤 BUILDING SIMPLE TTS HOTKEY" -ForegroundColor Yellow  
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check if the simple file exists
if (-not (Test-Path "tts_hotkey_simple.py")) {
    Write-Host "❌ ERROR: tts_hotkey_simple.py not found!" -ForegroundColor Red
    Write-Host "Make sure you are in the project root directory" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found: tts_hotkey_simple.py" -ForegroundColor Green

# Install minimal dependencies
Write-Host "📦 INSTALLING MINIMAL DEPENDENCIES..." -ForegroundColor Green
Write-Host "Only installing: requests, keyboard, pyinstaller" -ForegroundColor Yellow

try {
    & python -m pip install requests keyboard pyinstaller
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
    Write-Host "✅ Dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR installing dependencies!" -ForegroundColor Red
    Write-Host "Check if Python is available" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "🔨 BUILDING SIMPLE EXECUTABLE..." -ForegroundColor Green
Write-Host "This version has minimal dependencies for maximum compatibility" -ForegroundColor Yellow
Write-Host ""

# Build command with minimal hidden imports
$buildArgs = @(
    "--onefile",
    "--console", 
    "--name=tts_hotkey_simple",
    # Only essential imports
    "--hidden-import=requests",
    "--hidden-import=urllib3", 
    "--hidden-import=certifi",
    "--hidden-import=keyboard",
    "--hidden-import=threading",
    "--hidden-import=json",
    "tts_hotkey_simple.py"
)

# Add icon if available
if (Test-Path "icon.ico") {
    $buildArgs = @("--icon=icon.ico") + $buildArgs
    Write-Host "✅ Using icon: icon.ico" -ForegroundColor Green
} else {
    Write-Host "⚠️ No icon found - building without custom icon" -ForegroundColor Yellow
}

# Execute PyInstaller
try {
    & python -m PyInstaller @buildArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host "✅ SIMPLE EXECUTABLE BUILT SUCCESSFULLY!" -ForegroundColor Green
        Write-Host "=" * 60 -ForegroundColor Green
        Write-Host ""
        
        if (Test-Path "dist/tts_hotkey_simple.exe") {
            $exeSize = (Get-Item "dist/tts_hotkey_simple.exe").Length
            $exeSizeMB = [math]::Round($exeSize / 1MB, 2)
            
            Write-Host "📁 Location: dist/tts_hotkey_simple.exe" -ForegroundColor Cyan
            Write-Host "📏 Size: $exeSizeMB MB" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "🎯 FEATURES:" -ForegroundColor Yellow
            Write-Host "   ✅ Minimal dependencies (only requests + keyboard)" -ForegroundColor White
            Write-Host "   ✅ Maximum Windows compatibility" -ForegroundColor White
            Write-Host "   ✅ Discord bot integration" -ForegroundColor White
            Write-Host "   ✅ Hotkey support" -ForegroundColor White
            Write-Host "   ✅ Small file size" -ForegroundColor White
            Write-Host ""
            Write-Host "🚀 TO USE:" -ForegroundColor Yellow
            Write-Host "   1. Run: dist/tts_hotkey_simple.exe" -ForegroundColor White
            Write-Host "   2. Type {text} anywhere to speak" -ForegroundColor White
            Write-Host "   3. Works on any Windows PC" -ForegroundColor White
            Write-Host ""
            
            # Create a simple batch file
            $batContent = @"
@echo off
title TTS Hotkey - Simple Version
echo.
echo =======================================
echo   TTS HOTKEY - SIMPLE VERSION
echo =======================================
echo.
echo This is the minimal version with maximum compatibility
echo Works on any Windows computer!
echo.
echo Press any key to start...
pause >nul
echo.
dist\tts_hotkey_simple.exe
echo.
echo Application closed. Press any key to exit...
pause >nul
"@
            Set-Content -Path "run_tts_simple.bat" -Value $batContent -Encoding ASCII
            Write-Host "📝 Created run_tts_simple.bat for easy execution" -ForegroundColor Green
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
    Write-Host "Check the error messages above" -ForegroundColor Yellow
    exit 1
}

Write-Host "🎉 SIMPLE BUILD COMPLETED!" -ForegroundColor Green
Write-Host ""
Write-Host "💡 ADVANTAGES OF SIMPLE VERSION:" -ForegroundColor Yellow
Write-Host "   ✅ Smaller file size" -ForegroundColor White
Write-Host "   ✅ Fewer dependencies = fewer problems" -ForegroundColor White  
Write-Host "   ✅ Works on older Windows versions" -ForegroundColor White
Write-Host "   ✅ No audio libraries needed" -ForegroundColor White
Write-Host "   ✅ Just Discord integration via HTTP" -ForegroundColor White
Write-Host ""
Write-Host "📝 NEXT STEPS:" -ForegroundColor Yellow
Write-Host "1. Test: run_tts_simple.bat" -ForegroundColor White
Write-Host "2. Distribute: dist/tts_hotkey_simple.exe" -ForegroundColor White
Write-Host "3. Share with users - maximum compatibility!" -ForegroundColor White
Write-Host ""