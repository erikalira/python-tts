# tts-hotkey-windows

## Overview
This project is a text-to-speech hotkey application that allows users to input text using specific keyboard shortcuts and have it spoken aloud. It includes:
- **Discord Bot**: Joins voice channels and plays TTS messages
- **Hotkey App**: Captures text input (`{text here}`) and sends to Discord bot
- **Docker Support**: Deploys on Render with espeak-ng for high-quality TTS

## Features
- Capture text input using keyboard shortcuts
- Discord bot with slash commands (`/join`, `/leave`, `/speak`)
- TTS engine with automatic fallback (pyttsx3 → gTTS)
- Voice channel support with audio streaming
- Docker deployment for production
- Simple and intuitive interface

## Requirements

### Local Development (Windows)
- Python 3.11+
- FFmpeg (for Discord voice support)
- Virtual environment (recommended)

### Production (Render with Docker)
- Docker-enabled environment
- All dependencies installed via Dockerfile

Install Python dependencies:
```powershell
pip install -r requirements.txt
```

## Running the Application

### 🐳 Docker (Production - Render)

The application is configured to run with Docker on Render, which includes:
- **espeak-ng**: Native TTS engine (faster, offline)
- **FFmpeg**: Audio processing for Discord
- **Gunicorn**: Production WSGI server

**Automatic Deployment:**
1. Push to `main` branch triggers auto-deploy on Render
2. Render builds Docker image with all system dependencies
3. Container starts with gunicorn + Discord bot

**Manual Docker Build (Local Testing):**
```powershell
# Build the image
docker build -t tts-hotkey .

# Run locally (requires .env file with DISCORD_TOKEN)
docker run -p 10000:10000 --env-file .env tts-hotkey
```

### 💻 Local Development (Windows - No Docker)

Best for development and testing on Windows:

### 💻 Local Development (Windows - No Docker)

Best for development and testing on Windows:

**1. Create and activate virtual environment:**
```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**2. Install dependencies:**
```powershell
pip install -r requirements.txt
pip install pynacl  # For Discord voice support
```

**3. Install FFmpeg:**
- Download from https://www.gyan.dev/ffmpeg/builds/
- Extract and add `bin` folder to PATH
- Verify: `ffmpeg -version`

**4. Configure Discord token:**

Create `.env` file:
```env
DISCORD_TOKEN=your_token_here
DISCORD_BOT_URL=http://127.0.0.1:5000
```

Or set environment variables:
```powershell
$env:DISCORD_TOKEN = "YOUR_TOKEN_HERE"
$env:DISCORD_BOT_URL = "http://127.0.0.1:5000"
```

**5. Run the Discord bot:**
```powershell
python src\discord_bot.py
```

**6. Run the hotkey app (separate terminal):**
```powershell
python src\tts_hotkey.py
```

Type `{hello world}` in any application to trigger TTS.

### 🌐 Production with Gunicorn (Local Testing)

Test the production setup locally:

```powershell
# Using wsgi.py (Flask wrapper + Discord bot)
gunicorn --bind 0.0.0.0:10000 --workers 1 --threads 2 --timeout 120 wsgi:app

# Or using run_with_flask.py
python src\run_with_flask.py
```

This starts:
- Flask health endpoint on port 8080 (returns "Bot online!")
- Discord bot with `/speak` endpoint on port 5000


## Discord Bot Setup

1. **Create bot in Discord Developer Portal:**
   - Go to https://discord.com/developers/applications
   - Create new application → Bot section
   - Enable "Message Content Intent" and "Server Members Intent"
   - Copy the bot token

2. **Invite bot to server:**
   - OAuth2 → URL Generator
   - Scopes: `bot`, `applications.commands`
   - Permissions: `Connect`, `Speak`, `Use Voice Activity`
   - Use generated URL to invite

3. **Configure token:**
   - Add to `.env` file: `DISCORD_TOKEN=your_token_here`
   - Or set environment variable on Render

## TTS Engine Configuration

The bot supports two TTS engines with flexible configuration via environment variables:

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TTS_ENGINE` | `gtts` | Engine to use: `gtts` (Google TTS, best quality) or `pyttsx3` (espeak-ng, offline) |
| `TTS_LANGUAGE` | `pt` | Language code for gTTS (e.g., `pt`, `en`, `es`, `fr`) |
| `TTS_VOICE_ID` | `roa/pt-br` | Voice ID for pyttsx3/espeak-ng (e.g., `roa/pt-br`, `en-us`, `roa/es`) |

### Configuration Examples

**Default (gTTS with Portuguese):**
```env
TTS_ENGINE=gtts
TTS_LANGUAGE=pt
```

**espeak-ng with Portuguese (Brazil):**
```env
TTS_ENGINE=pyttsx3
TTS_VOICE_ID=roa/pt-br
```

**gTTS with English:**
```env
TTS_ENGINE=gtts
TTS_LANGUAGE=en
```

**espeak-ng with Spanish:**
```env
TTS_ENGINE=pyttsx3
TTS_VOICE_ID=roa/es
```

### Available espeak-ng Voices

espeak-ng provides 200+ voices across many languages. Common voice IDs:
- Portuguese (Brazil): `roa/pt-br`
- Portuguese (Portugal): `roa/pt`
- English (US): `en-us`
- English (UK): `en-gb`
- Spanish: `roa/es`
- French: `roa/fr`
- German: `gmw/de`
- Italian: `roa/it`
- Japanese: `ja`
- Chinese (Mandarin): `sit/cmn`

To see all available voices, check the startup logs when using `TTS_ENGINE=pyttsx3`.

### Configuring on Render

1. Go to Render Dashboard → Your Service → Environment
2. Add environment variables:
   - `TTS_ENGINE` = `gtts` (or `pyttsx3`)
   - `TTS_LANGUAGE` = `pt` (or your preferred language)
   - `TTS_VOICE_ID` = `roa/pt-br` (if using pyttsx3)
3. Save changes (triggers automatic redeploy)

## Discord Bot Commands

Once the bot is running:
- `/join` - Bot joins your current voice channel
- `/leave` - Bot leaves the voice channel
- `/speak <text>` - Bot speaks the provided text
- `/config` - Configure TTS settings for your server (Admin only)

### Using `/config` Command

**View current configuration:**
```
/config
```

**Change to gTTS with English:**
```
/config engine:gtts language:en
```

**Change to espeak-ng with Portuguese (Brazil):**
```
/config engine:pyttsx3 voice_id:roa/pt-br
```

**Change to espeak-ng with Spanish:**
```
/config engine:pyttsx3 voice_id:roa/es
```

**Note:** Configuration set via `/config` is temporary and resets when the bot restarts. For permanent settings, use environment variables on Render.

## Architecture

```
┌─────────────────┐
│  Hotkey App     │  (Windows local)
│  tts_hotkey.py  │  Captures {text} input
└────────┬────────┘
         │ POST /speak
         ▼
┌─────────────────┐
│  Discord Bot    │  (Render Docker container)
│  discord_bot.py │  ← espeak-ng TTS engine
└────────┬────────┘  ← FFmpeg audio processing
         │
         ▼
┌─────────────────┐
│  Discord Voice  │
│  Channel        │  Audio playback
└─────────────────┘
```

## Deployment (Render)

### Files for Docker Deployment:
- `Dockerfile` - Installs espeak-ng, ffmpeg, Python deps
- `render.yaml` - Render configuration (env: docker)
- `.dockerignore` - Excludes unnecessary files from build

### Automatic Deployment:
1. Push to `main` branch on GitHub
2. Render detects changes and builds Docker image
3. Deploys container with all dependencies
4. Bot auto-connects to Discord

### Environment Variables on Render:
Set in Render dashboard:
- `DISCORD_TOKEN` - Your bot token (required)
- `PORT` - Set to `10000` (default)

### TTS Engine Behavior:
- **Local (Windows)**: Uses pyttsx3 with SAPI5
- **Render (Docker)**: Uses pyttsx3 with espeak-ng
- **Fallback**: Uses gTTS (Google) if pyttsx3 fails

## Testing

### Test Discord Bot Endpoint:
```powershell
$body = @{ text = "Hello from test" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5000/speak -Body $body -ContentType 'application/json'
```

### Test Hotkey App:
1. Run `python src\tts_hotkey.py`
2. Type `{hello world}` in any text editor
3. Bot should speak in Discord voice channel

## Troubleshooting

## Troubleshooting

### Common Issues:

**`ModuleNotFoundError: No module named 'aiohttp'`**
```powershell
pip install -r requirements.txt
```

**`PyNaCl library needed in order to use voice`**
```powershell
pip install pynacl
```

**Virtual environment activation fails:**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

**Hotkey not triggering bot:**
- Check `DISCORD_BOT_URL` environment variable
- Verify bot is running: `http://127.0.0.1:5000`
- Check hotkey logs for POST response

**FFmpeg not found:**
- Download from https://www.gyan.dev/ffmpeg/builds/
- Add to PATH or place `ffmpeg.exe` in project root
- Verify: `ffmpeg -version`

**Docker build fails on Render:**
- Check logs in Render dashboard
- Verify `Dockerfile` has correct dependencies
- Ensure `render.yaml` has `env: docker`

**Bot not speaking in Discord:**
- Use `/join` command first
- Check bot has `Connect` and `Speak` permissions
- Verify FFmpeg is installed
- Check Render logs for TTS errors

### Render Logs:
```powershell
# Using MCP (if configured)
# Ask in Copilot Chat: "Mostre os logs do serviço python-tts"
```

## Notes / Security

- **Never commit** your Discord token to the repository
- Use `.env` file for local development (already in `.gitignore`)
- Set environment variables in Render dashboard for production
- `setx` persists variables (new shells only); use `$env:` for current shell


## Building Windows Executable

Create a standalone `.exe` for Windows distribution:

**Prerequisites:**
```powershell
pip install pyinstaller
```

**Option A - PowerShell script (recommended):**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\build_exe.ps1
```

**Option B - Batch script:**
```cmd
.\build_exe.bat
```

**Option C - Manual PyInstaller:**
```powershell
cd src
pyinstaller --onefile --noconsole tts_hotkey.py
# Executable: src\dist\tts_hotkey.exe
```

**Result:** `tts_hotkey.exe` in project root

### Build Troubleshooting:
- **Missing modules**: Add `--hidden-import modulename`
- **Missing data**: Use `--add-data "file;dest"`
- **AV warnings**: Code-signing recommended
- **Runtime errors**: Install Visual C++ Redistributable

## Project Structure

```
tts-hotkey-windows/
├── src/
│   ├── discord_bot.py      # Discord bot with TTS
│   ├── tts_hotkey.py       # Windows hotkey app
│   └── run_with_flask.py   # Flask wrapper (optional)
├── Dockerfile              # Docker image with espeak-ng
├── .dockerignore          # Docker build exclusions
├── render.yaml            # Render deployment config
├── render-build.sh        # Build script (Docker handles deps)
├── wsgi.py               # Gunicorn entry point
├── requirements.txt      # Python dependencies
├── .env.example         # Environment template
└── README.md           # This file
```

## Contributing
Fork the repository and submit pull requests for improvements or bug fixes.

## License
This project is licensed under the MIT License.