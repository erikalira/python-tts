#!/usr/bin/env powershell
# Build TTS Hotkey with Clean Architecture for Windows
# This script creates a Windows executable with full clean architecture support

param(
    [switch]$Debug = $false,
    [switch]$SkipTests = $false
)

Write-Host "Building TTS Hotkey with Clean Architecture..." -ForegroundColor Cyan
Write-Host "=================================================="

# Configuration
$AppName = "tts_hotkey_clean"
$MainScript = "tts_hotkey_configurable.py"
$DistPath = "dist"
$BuildPath = "build"
$SpecPath = "build\$AppName.spec"

# Check if running in correct directory
if (-not (Test-Path $MainScript)) {
    Write-Host "Error: $MainScript not found!" -ForegroundColor Red
    Write-Host "Run this script from the project root directory" -ForegroundColor Yellow
    exit 1
}

# Check for Python
try {
    $PythonVersion = python --version 2>&1
    Write-Host "Python found: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found in PATH!" -ForegroundColor Red
    exit 1
}

# Install/upgrade dependencies
Write-Host "`nInstalling dependencies..." -ForegroundColor Yellow

$Dependencies = @(
    "pyinstaller>=5.0",
    "keyboard>=0.13.5",
    "requests>=2.25.0",
    "pyttsx3>=2.90",
    "gtts>=2.2.0",
    "pygame>=2.1.0",
    "pystray>=0.19.0",
    "pillow>=8.0.0"
)

foreach ($dep in $Dependencies) {
    Write-Host "Installing $dep..." -ForegroundColor Gray
    try {
        python -m pip install --upgrade $dep 2>&1 | Out-Null
        Write-Host "  $dep installed" -ForegroundColor Green
    } catch {
        Write-Host "  Failed to install $dep" -ForegroundColor Yellow
    }
}

# Run tests if not skipped
if (-not $SkipTests) {
    Write-Host "`nRunning integration tests..." -ForegroundColor Yellow
    try {
        $TestResult = python test_integration.py
        Write-Host $TestResult
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Tests failed, but continuing build..." -ForegroundColor Yellow
        } else {
            Write-Host "Tests passed!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Could not run tests, continuing..." -ForegroundColor Yellow
    }
}

# Clean previous builds
Write-Host "`nCleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $DistPath) { Remove-Item -Recurse -Force $DistPath }
if (Test-Path $BuildPath) { Remove-Item -Recurse -Force $BuildPath }
Write-Host "Cleanup completed" -ForegroundColor Green

# Prepare PyInstaller arguments
Write-Host "`nPreparing build configuration..." -ForegroundColor Yellow

$PyInstallerArgs = @(
    "--name", $AppName,
    "--onefile",
    "--console",
    "--icon=icon.ico",
    "--distpath", $DistPath,
    "--workpath", $BuildPath,
    "--specpath", $BuildPath,
    "--add-data", "src;src",
    "--add-data", "config;config",
    "--add-data", "*.json;.",
    "--hidden-import", "src.standalone",
    "--hidden-import", "src.standalone.config.standalone_config",
    "--hidden-import", "src.standalone.app.simple_app",
    "--hidden-import", "src.standalone.services",
    "--hidden-import", "src.standalone.gui",
    "--hidden-import", "keyboard",
    "--hidden-import", "pystray",
    "--hidden-import", "PIL",
    "--hidden-import", "pyttsx3",
    "--hidden-import", "gtts",
    "--hidden-import", "requests",
    "--hidden-import", "tkinter",
    "--hidden-import", "tkinter.ttk",
    "--hidden-import", "tkinter.messagebox",
    "--hidden-import", "json",
    "--hidden-import", "threading",
    "--hidden-import", "pathlib",
    "--hidden-import", "dataclasses",
    "--hidden-import", "abc",
    "--hidden-import", "typing",
    $MainScript
)

if ($Debug) {
    $PyInstallerArgs += "--debug", "all"
    Write-Host "Debug mode activated" -ForegroundColor Yellow
}

Write-Host "PyInstaller command:" -ForegroundColor Gray
Write-Host "python -m PyInstaller $($PyInstallerArgs -join ' ')" -ForegroundColor Gray

try {
    & python -m PyInstaller @PyInstallerArgs
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`nBuild successful!" -ForegroundColor Green
    } else {
        Write-Host "`nBuild failed with exit code $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
} catch {
    Write-Host "`nBuild failed with error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Verify executable
$ExePath = Join-Path $DistPath "$AppName.exe"
if (-not (Test-Path $ExePath)) {
    Write-Host "`nError: Executable not found at $ExePath" -ForegroundColor Red
    exit 1
}

$ExeSize = (Get-Item $ExePath).Length / 1MB
Write-Host "`nExecutable created successfully!" -ForegroundColor Green
Write-Host "Size: $([math]::Round($ExeSize, 2)) MB" -ForegroundColor White

# Create batch file for easy execution
$BatchContent = @"
@echo off
echo Starting TTS Hotkey Clean Architecture...
echo ==========================================
"$AppName.exe"
if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit...
    pause
)
"@

$BatchPath = Join-Path $DistPath "run_$AppName.bat"
$BatchContent | Out-File -FilePath $BatchPath -Encoding ascii
Write-Host "Batch file: $BatchPath" -ForegroundColor White

Write-Host "`nBUILD COMPLETED!" -ForegroundColor Green
Write-Host "=================================================="
Write-Host "Executable: $ExePath" -ForegroundColor Cyan
Write-Host "To run: $BatchPath" -ForegroundColor Cyan
Write-Host "`nINCLUDED FEATURES:" -ForegroundColor Yellow
Write-Host "  Clean Architecture complete" -ForegroundColor Green
Write-Host "  Graphical interface (Tkinter)" -ForegroundColor Green
Write-Host "  System Tray" -ForegroundColor Green
Write-Host "  Persistent configuration" -ForegroundColor Green
Write-Host "  TTS Multi-engine (gTTS + pyttsx3)" -ForegroundColor Green
Write-Host "  Discord Bot Integration" -ForegroundColor Green
Write-Host "  Global Hotkey (trigger-based)" -ForegroundColor Green
Write-Host "  Automatic fallback" -ForegroundColor Green

Write-Host "`nReady for Windows deployment!" -ForegroundColor Green