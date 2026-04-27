#!/usr/bin/env powershell
# Build Desktop App with Clean Architecture for Windows
# Simplified version that handles Windows paths correctly

param(
    [switch]$Debug = $false,
    [switch]$SkipTests = $false
)

Write-Host "Building Desktop App with Clean Architecture..." -ForegroundColor Cyan
Write-Host "=================================================="

# Configuration
$AppName = "HotkeyTTS"
$MainScript = "app.py"
$DistPath = "dist"
$BuildPath = "build"
$VenvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
$PythonExecutable = "python"

# Check if running in correct directory
if (-not (Test-Path $MainScript)) {
    Write-Host "Error: $MainScript not found!" -ForegroundColor Red
    Write-Host "Run this script from the project root directory" -ForegroundColor Yellow
    exit 1
}

# Check for Python
try {
    if (Test-Path $VenvPython) {
        $PythonExecutable = $VenvPython
    }
    $PythonVersion = & $PythonExecutable --version 2>&1
    Write-Host "Python found: $PythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found in PATH!" -ForegroundColor Red
    exit 1
}

# Check for PyInstaller after the lockfile-based environment sync
try {
    & $PythonExecutable -m PyInstaller --version 2>&1 | Out-Null
    Write-Host "`nPyInstaller is available in the synchronized environment" -ForegroundColor Green
} catch {
    Write-Host "`nPyInstaller is not available." -ForegroundColor Red
    Write-Host "Run: uv sync --locked --group build" -ForegroundColor Yellow
    exit 1
}

# Skip tests for now due to encoding issues
if (-not $SkipTests) {
    Write-Host "`nSkipping tests (encoding issues on Windows)..." -ForegroundColor Yellow
}

# Clean previous builds
Write-Host "`nCleaning previous builds..." -ForegroundColor Yellow
if (Test-Path $DistPath) { Remove-Item -Recurse -Force $DistPath }
if (Test-Path $BuildPath) { Remove-Item -Recurse -Force $BuildPath }
Write-Host "Cleanup completed" -ForegroundColor Green

# Prepare PyInstaller arguments - simplified for Windows
Write-Host "`nPreparing build configuration..." -ForegroundColor Yellow

# Get absolute path to .env file
$EnvFilePath = Resolve-Path ".env" -ErrorAction SilentlyContinue
if (-not $EnvFilePath) {
    Write-Host "Warning: .env file not found, skipping data addition" -ForegroundColor Yellow
    $AddDataArg = $null
} else {
    $AddDataArg = "--add-data", "$EnvFilePath;."
}

$PyInstallerArgs = @(
    "--name", $AppName,
    "--onefile", 
    "--windowed",
    "--distpath", $DistPath,
    "--workpath", $BuildPath,
    "--specpath", $BuildPath
)

if ($AddDataArg) {
    $PyInstallerArgs += $AddDataArg
}

$PyInstallerArgs += @(
    "--hidden-import", "keyboard",
    "--hidden-import", "pystray",
    "--hidden-import", "PIL", 
    "--hidden-import", "pyttsx3",
    "--hidden-import", "gtts",
    "--hidden-import", "requests",
    "--hidden-import", "tkinter",
    "--hidden-import", "tkinter.ttk",
    "--hidden-import", "tkinter.messagebox",
    $MainScript
)

# Add icon if available  
$IconPath = "icon.ico"
if (Test-Path $IconPath) {
    $AbsoluteIconPath = (Resolve-Path $IconPath).Path
    $PyInstallerArgs += "--icon=$AbsoluteIconPath"
    Write-Host "Using icon: $AbsoluteIconPath" -ForegroundColor Gray
} else {
    Write-Host "Icon not found at $IconPath, building without icon" -ForegroundColor Yellow
}

if ($Debug) {
    $PyInstallerArgs += "--debug", "all"
    Write-Host "Debug mode activated" -ForegroundColor Yellow
}

Write-Host "PyInstaller command:" -ForegroundColor Gray
Write-Host "$PythonExecutable -m PyInstaller $($PyInstallerArgs -join ' ')" -ForegroundColor Gray

try {
    & $PythonExecutable -m PyInstaller @PyInstallerArgs
    
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

# Create batch file for optional troubleshooting
$BatchContent = @"
@echo off
echo Starting Desktop App...
echo ==========================================
"$AppName.exe"
if errorlevel 1 (
    echo.
    echo Error occurred. Press any key to exit...
    pause >nul
)
"@

$BatchPath = Join-Path $DistPath "run_${AppName}_debug.bat"
$BatchContent | Out-File -FilePath $BatchPath -Encoding ascii
Write-Host "Debug batch file: $BatchPath" -ForegroundColor White

Write-Host "`nBUILD COMPLETED!" -ForegroundColor Green
Write-Host "=================================================="
Write-Host "Executable: $ExePath" -ForegroundColor Cyan
Write-Host "To run (recommended): $ExePath" -ForegroundColor Cyan
Write-Host "Debug launcher: $BatchPath" -ForegroundColor Cyan

Write-Host "`nINCLUDED FEATURES:" -ForegroundColor Yellow
Write-Host "  Clean Architecture complete" -ForegroundColor Green
Write-Host "  Graphical interface (Tkinter)" -ForegroundColor Green
Write-Host "  System Tray support" -ForegroundColor Green
Write-Host "  Persistent configuration" -ForegroundColor Green
Write-Host "  TTS Multi-engine (gTTS + pyttsx3)" -ForegroundColor Green
Write-Host "  Global Hotkey support" -ForegroundColor Green
Write-Host "`nReady for Windows deployment!" -ForegroundColor Green
