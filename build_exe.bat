@echo off
REM This batch script builds the executable for the TTS Hotkey application using PyInstaller.

REM Navigate to the src directory
cd src

REM Use PyInstaller to create the executable
pyinstaller --onefile --noconsole tts_hotkey.py

REM Move the executable to the root directory
move dist\tts_hotkey.exe ..\

REM Clean up the build files
cd ..
rmdir /s /q build
rmdir /s /q dist
del tts_hotkey.spec

echo Build complete. The executable is located in the root directory.