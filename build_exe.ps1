# PowerShell script to build the executable using PyInstaller

# Navigate to the src directory
Set-Location -Path ".\src"

# Build the executable using PyInstaller with icon
# --noconsole: no console window
# --icon: use the icon file
# --add-data: include icon.png for runtime
$iconPath = "..\icon.ico"
$iconDataPath = "..\icon.png;."
$pyinstaller = "..\.venv\Scripts\pyinstaller.exe"

if (Test-Path $iconPath) {
    & $pyinstaller --onefile --noconsole --icon="$iconPath" --add-data="$iconDataPath" tts_hotkey.py
} else {
    Write-Host "⚠️ icon.ico not found, building without custom icon"
    & $pyinstaller --onefile --noconsole tts_hotkey.py
}

# Move the executable to the root directory if it was created
if (Test-Path ".\dist\tts_hotkey.exe") {
	Move-Item -Path ".\dist\tts_hotkey.exe" -Destination "..\tts_hotkey.exe" -Force
	Write-Host "✅ Executable created: tts_hotkey.exe"
}

# Clean up the build files (only if they exist)
if (Test-Path ".\build") { Remove-Item -Recurse -Force ".\build" }
if (Test-Path ".\dist") { Remove-Item -Recurse -Force ".\dist" }
if (Test-Path ".\tts_hotkey.spec") { Remove-Item -Force ".\tts_hotkey.spec" }