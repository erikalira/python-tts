# PowerShell script to build the Discord TTS Bot executable using PyInstaller

Write-Host "🚀 Building Discord TTS Bot executable..." -ForegroundColor Yellow
Write-Host ""

# Check if the main file exists
if (-not (Test-Path "main.py")) {
    Write-Host "❌ ERROR: main.py not found!" -ForegroundColor Red
    Write-Host "Make sure you are in the correct directory" -ForegroundColor Yellow
    exit 1
}

# Install dependencies if requirements.txt exists
if (Test-Path "requirements.txt") {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Green
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "⚠️ requirements.txt not found" -ForegroundColor Yellow
}

# Install PyInstaller if not available
Write-Host "🔧 Checking PyInstaller..." -ForegroundColor Green
try {
    $null = & python -m PyInstaller --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller not found"
    }
} catch {
    Write-Host "Installing PyInstaller..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Build the executable
Write-Host "🔨 Building executable..." -ForegroundColor Green

$iconPath = "icon.ico"
$buildCommand = @(
    "python", "-m", "PyInstaller",
    "--onefile",
    "--console",
    "--name=discord_tts_bot",
    "--hidden-import=discord",
    "--hidden-import=discord.ext",
    "--hidden-import=discord.ext.commands",
    "--hidden-import=flask",
    "--hidden-import=gtts",
    "--hidden-import=pyttsx3",
    "--hidden-import=requests",
    "--hidden-import=urllib3",
    "--hidden-import=certifi",
    "--hidden-import=python_dotenv"
)

# Add icon if it exists
if (Test-Path $iconPath) {
    $buildCommand += "--icon=$iconPath"
    Write-Host "✅ Using custom icon: $iconPath" -ForegroundColor Green
} else {
    Write-Host "⚠️ icon.ico not found, building without custom icon" -ForegroundColor Yellow
}

# Add the main file
$buildCommand += "main.py"

# Execute the build command
& $buildCommand[0] $buildCommand[1..($buildCommand.Length-1)]

if ($LASTEXITCODE -eq 0) {
    # Move the executable to the root directory if it was created
    if (Test-Path "dist\discord_tts_bot.exe") {
        Write-Host "✅ Executable created successfully!" -ForegroundColor Green
        Write-Host "📁 Location: dist\discord_tts_bot.exe" -ForegroundColor Cyan
        
        # Create a simple batch file to run the exe with proper environment
        $batContent = @"
@echo off
echo Starting Discord TTS Bot...
echo Make sure you have a valid .env file with Discord token!
echo.
dist\discord_tts_bot.exe
pause
"@
        Set-Content -Path "run_discord_bot.bat" -Value $batContent -Encoding ASCII
        Write-Host "📝 Created run_discord_bot.bat for easy execution" -ForegroundColor Green
    } else {
        Write-Host "❌ Executable not found in dist directory" -ForegroundColor Red
    }
} else {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🎉 Build completed!" -ForegroundColor Green
Write-Host "To run the bot:" -ForegroundColor Yellow
Write-Host "1. Make sure you have a .env file with DISCORD_TOKEN" -ForegroundColor White
Write-Host "2. Run: run_discord_bot.bat" -ForegroundColor White
Write-Host "3. Or directly: dist\discord_tts_bot.exe" -ForegroundColor White