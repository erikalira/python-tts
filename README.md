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

This README below adds step-by-step setup for the Discord bot, voice support and troubleshooting.

## Full Setup (Windows)

Follow these steps from the project root (where `requirements.txt` and `.venv` live).

1) Create a virtual environment (if you don't have one):

```powershell
python -m venv .venv
```

2) Activate the venv (PowerShell):

```powershell
Set-Location <project-root>
# allow script execution for the session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
& .\.venv\Scripts\Activate.ps1
```

If you prefer not to activate, you can invoke the venv python directly:

```powershell
.\.venv\Scripts\python.exe src\discord_bot.py
```

3) Install Python dependencies:

```powershell
pip install -r requirements.txt
# For voice support (discord.py voice) also install PyNaCl:
pip install pynacl
```

4) Install `ffmpeg` and add to PATH (required by the bot to stream audio to Discord):

- Download a static Windows build (eg. from https://www.gyan.dev/ffmpeg/builds/ or https://ffmpeg.org/download.html).
- Unzip and add the `bin` folder to your Windows `PATH` (or place `ffmpeg.exe` somewhere on PATH).
- Verify with:

```powershell
ffmpeg -version
```

5) Configure Discord bot token and (optional) local bot URL

- Create a bot in the Discord Developer Portal, invite it to your server with `applications.commands` + `bot` scopes and the `Connect/Speak` permissions.
- Set the token (temporary for current shell):

```powershell
$env:DISCORD_TOKEN = "YOUR_TOKEN_HERE"
```

- (Optional) Persist the token in Windows environment variables:

```powershell
setx DISCORD_TOKEN "YOUR_TOKEN_HERE"
```

- If you run the bot locally and want the hotkey app to send TTS to it, set the bot URL in the same shell you will run `tts_hotkey.py` from:

```powershell
$env:DISCORD_BOT_URL = 'http://127.0.0.1:5000'
```

6) Run the Discord bot (from project root):

```powershell
python src\discord_bot.py
```

Expected output: `Discord bot ready as <name>` and `Slash commands synced` (or a message about sync failure).

7) Run the TTS hotkey app (in a separate shell where you set `DISCORD_BOT_URL` if you want bot playback):

```powershell
python src\tts_hotkey.py
```

Type `{hello world}` in any application to trigger speech. When `DISCORD_BOT_URL` is set the hotkey will try to POST the text to the bot endpoint and skip local playback if the bot responds with success.

## Quick Manual Tests

- Test the bot endpoint directly (without using the hotkey):

```powershell
#$body = @{ text = "Olá do teste" } | ConvertTo-Json
#Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/speak -Body $body -ContentType 'application/json'
```

If the bot plays audio in the target Discord voice channel the endpoint is working.

## Troubleshooting

- `ModuleNotFoundError: No module named 'aiohttp'` — install dependencies: `pip install -r requirements.txt` or `pip install aiohttp`.
- `Could not join channel: PyNaCl library needed in order to use voice` — run `pip install pynacl` in the venv.
- `'.\.venv\Scripts\Activate.ps1' is not recognized` — you are likely in the `src` folder; change to project root and run the activate command. Verify the venv exists with `Test-Path .\.venv\Scripts\Activate.ps1`.
- If hotkey still plays locally: check the `DISCORD_BOT_URL` environment variable in the shell where you run `tts_hotkey.py` and check the hotkey logs — it prints lines like:

```
[tts_hotkey] POST -> http://127.0.0.1:5000/speak payload={'text': '...'}
[tts_hotkey] bot response: 200 'ok'
```

If the bot response is non-200, the hotkey falls back to local playback and prints the response body.

## Notes / Security

- Keep your bot token secret. Do not commit it to the repo.
- When you run `setx` to persist environment variables, new shells will see the variable; existing shells need the temporary `$env:...` assignment.


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