# tts-hotkey-windows

## Overview
This project is a text-to-speech hotkey application that allows users to input text using specific keyboard shortcuts and have it spoken aloud. It utilizes the `pyttsx3` library for text-to-speech functionality and the `keyboard` library to capture key events.

## Features
- Capture text input using keyboard shortcuts.
- Convert the captured text to speech.
- Simple and intuitive interface.

## Requirements
To run this project, you need to install the following dependencies:

- `keyboard`
- `pyttsx3`

You can install the required packages using pip:

```
pip install -r requirements.txt
```

## Usage
1. Run the application by executing the `src/tts_hotkey.py` script.
2. To input text, type `{your text here}` using the specified hotkey.
3. The application will read the text aloud.
4. Press `ESC` to exit the application.

## **Building The Executable**
Below are precise, tested steps to create a standalone `*.exe` on Windows using PowerShell (the project already includes helper scripts).

- **Prerequisites**: Python 3.8+ and a virtual environment (recommended).

- **From the project root** (where `requirements.txt`, `build_exe.ps1` and `build_exe.bat` live) run:

```powershell
# activate the virtual environment (only if you created it at `.venv`)
.\.venv\Scripts\Activate.ps1

# upgrade pip and install dependencies + PyInstaller
python -m pip install --upgrade pip
pip install -r .\requirements.txt
pip install pyinstaller
```

- **Option A — use the provided PowerShell script (recommended)**:

```powershell
# allow script execution for this session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# run the build script from the project root
.\build_exe.ps1
```

This script will call PyInstaller from inside `src\` and, if successful, move the generated executable to the project root as `tts_hotkey.exe`.

- **Option B — use the provided batch script**:

```powershell
# run from project root (Command Prompt or PowerShell)
.\build_exe.bat
```

- **Option C — run PyInstaller manually** (gives more control):

```powershell
# change to the src folder
Set-Location -Path .\src

# create a single-file, no-console executable
pyinstaller --onefile --noconsole tts_hotkey.py

# after success the exe will be in .\dist\tts_hotkey.exe
```

**Where the result appears**: after a successful build the executable will be in the project root as `tts_hotkey.exe` (or in `src\dist\tts_hotkey.exe` before being moved).

**Troubleshooting / Tips**
- **Missing modules at runtime**: if PyInstaller fails due to dynamically imported modules, add `--hidden-import modulename` or add them in the spec file.
- **Missing data files**: include with `--add-data "path\to\file;dest_folder"` or list them in the spec `datas` section.
- **PowerShell blocked**: use `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` (temporary for the session).
- **Antivirus warnings**: newly built EXEs can trigger AV heuristics; code-signing is recommended for broad distribution.
- **Visual C++ runtime**: if the EXE complains on another machine, install the Microsoft Visual C++ Redistributable.

If you want, I can also add `pyinstaller` to `requirements.txt` so future installs include it automatically.

## Contributing
Feel free to fork the repository and submit pull requests for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.