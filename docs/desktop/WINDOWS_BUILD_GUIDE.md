# Windows Build Guide

This guide explains how to create the Windows executable for the Desktop App with Clean Architecture.

## Prerequisites

- Python 3.11+ installed on Windows
- Windows 10/11
- `.venv` created and activated before installing dependencies

Recommended setup before the build:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Desktop App Clean Architecture

- File: `app.py`
- Architecture: Clean Architecture
- Characteristics:
  - Tkinter GUI with system tray integration
  - persistent JSON configuration
  - dependency injection across layers
  - automatic fallback if primary initialization fails

## Compile For Windows

```powershell
scripts\build\build_clean_architecture.ps1
```

## Executable Location

After compilation:

```text
dist/
|-- HotkeyTTS.exe
`-- run_HotkeyTTS_debug.bat
```

## Use The Executable

After the build:

```powershell
cd dist
.\HotkeyTTS.exe
```

On first run:

1. Configure the Discord User ID
2. Choose the TTS engine
3. Define the hotkeys
4. Save the configuration
5. Start the app from the tray

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Build fails | Activate `.venv` and reinstall dependencies with `pip install -r requirements.txt` |
| Icon not found | Check `assets/icon.ico`. If needed, recreate it with `python scripts/utils/create_icon.py` and run the official script again |
| PyInstaller not found | With `.venv` active, run `pip install pyinstaller` |
| Antivirus blocks `.exe` | Add an exception for the `dist/` directory |

## Distribution

The Desktop App executable is portable:

- Copy `dist/HotkeyTTS.exe`
- It works on Windows 10/11
- It saves configuration under `AppData/Local/DesktopApp/`
