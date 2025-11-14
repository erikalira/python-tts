# PowerShell script to build the executable using PyInstaller

# Navigate to the src directory
Set-Location -Path ".\src"

# Build the executable using PyInstaller (call the script file directly, not a .spec)
pyinstaller --onefile --noconsole tts_hotkey.py

# Move the executable to the root directory if it was created
if (Test-Path ".\dist\tts_hotkey.exe") {
	Move-Item -Path ".\dist\tts_hotkey.exe" -Destination "..\tts_hotkey.exe"
}

# Clean up the build files (only if they exist)
if (Test-Path ".\build") { Remove-Item -Recurse -Force ".\build" }
if (Test-Path ".\dist") { Remove-Item -Recurse -Force ".\dist" }
if (Test-Path ".\tts_hotkey.spec") { Remove-Item -Force ".\tts_hotkey.spec" }