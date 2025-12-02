# tts-hotkey-windows

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

## Overview

This project is a text-to-speech hotkey application that allows users to input text using specific keyboard shortcuts and have it spoken aloud. Built with **Clean Architecture** and **SOLID principles**, it includes:

- **Discord Bot**: Joins voice channels and plays TTS messages
- **Standalone App**: Complete Windows application with GUI and system tray
- **Hotkey System**: Captures text input (`{text here}`) with global shortcuts
- **Clean Architecture**: Fully implemented with proper separation of concerns
- **Docker Support**: Deploys on Render with espeak-ng for high-quality TTS

## Features

**🏗️ Clean Architecture & SOLID Principles**

- Full separation of concerns across layers
- Dependency injection and inversion of control
- Single responsibility principle throughout
- Interface segregation and clean abstractions

**🎯 Core Functionality**

- Capture text input using keyboard shortcuts
- Discord bot with slash commands (`/join`, `/leave`, `/speak`)
- TTS engine with automatic fallback (pyttsx3 → gTTS)
- Voice channel support with audio streaming
- System tray integration with notifications
- Persistent configuration management

**🚀 Deployment Options**

- Windows standalone executable (.exe)
- Docker deployment for production
- Cross-platform compatibility (Windows/Linux)
- Simple and intuitive interface

## 🏆 TTS Hotkey Clean Architecture (Standalone)

**For users who want a single `.exe` file with Clean Architecture and SOLID principles:**

- 📄 **[`README_STANDALONE.md`](docs/README_STANDALONE.md)** - Complete standalone guide
- 🏗️ **Clean Architecture** - Full separation of concerns and SOLID principles
- ⚙️ **Configuration Management** - Dataclass-based with GUI interface
- 🎯 **Service Layer** - TTS, Hotkey, and Notification services
- 💾 **Repository Pattern** - JSON-based configuration persistence
- 🖥️ **Platform Support** - Windows (full features) + Linux (graceful degradation)
- 📊 **System Integration** - System tray, global hotkeys, notifications
- ⚡ **Automatic Fallback** - Embedded implementation if clean architecture fails

```powershell
# Build Clean Architecture version
make build-clean
# OR: powershell scripts/build/build_clean_architecture.ps1

# Clean Architecture executable ready!
dist/tts_hotkey_clean.exe
```

**Architecture Layers:**

- **Config Layer**: `StandaloneConfig` with validation and persistence
- **Service Layer**: `TTSProcessor`, `HotkeyManager`, `SystemTrayService`
- **Application Layer**: `SimpleApplication` with dependency injection
- **Interface Layer**: Tkinter GUI and console interfaces

## 📁 Organized Scripts

All build and test scripts are now organized in the `scripts/` directory:

```
scripts/
├── build/          # Build scripts (PowerShell)
├── test/           # Test scripts
├── utils/          # Utilities (icon creation, etc.)
└── README.md       # Detailed scripts documentation
```

**Quick commands:**

```bash
# See all available commands
make help
# OR: ./scripts.sh help

# Most common usage
make install        # Install dependencies
make test          # Run tests
make build-exe     # Build executable
make clean         # Clean artifacts

# Alternative bash interface
./scripts.sh install
./scripts.sh test
./scripts.sh build-exe
```

📋 **See [`scripts/README.md`](scripts/README.md) for complete documentation.**

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
- **Flask keep-alive**: Health and `/speak` HTTP endpoint via `src.app`

Entrypoint: `python3 main.py` (no Gunicorn/WSGI). The Discord bot starts and the Flask server binds to `0.0.0.0:$PORT` (default `10000`).

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
python -m src.bot
```

O bot iniciará automaticamente o servidor HTTP na porta configurada.

**6. Run the hotkey app (Windows System Tray):**

```powershell
# Em outro terminal
python src\tts_hotkey.py
```

O aplicativo aparecerá na **bandeja do sistema** (system tray) do Windows com um ícone de microfone! 🎤

**Como usar:**

- Digite `{hello world}` em **qualquer aplicativo Windows** e o bot falará no Discord!
- **Clique com botão direito** no ícone da bandeja para ver opções
- Escolha **Exit** para fechar o aplicativo
- Não precisa mais usar `del` para sair - use o menu da bandeja!

### 🎯 Criando Executável (.exe) para Windows

Para criar um executável standalone que não precisa do Python instalado:

```bash
# Opção 1: Usando Makefile (Clean Architecture)
make build-clean

# Opção 2: PowerShell direto (Clean Architecture)
powershell scripts/build/build_clean_architecture.ps1
```

Isso criará `tts_hotkey.exe` na pasta raiz. Você pode:

- ✅ Executar direto (duplo clique) - abre na bandeja do sistema
- ✅ Adicionar ao **Iniciar com o Windows** (pasta `shell:startup`)
- ✅ Distribuir para outros computadores (não precisa Python instalado)
- ✅ Ícone customizado aparece na bandeja e no executável

### 🌐 HTTP Endpoints

When running (`python3 main.py` or Docker container):

- `GET /` → `{ status: "online", ... }`
- `GET /health` → `{ status: "healthy" }`
- `GET /version` → project metadata
- `GET /about` → basic service info
- `POST /speak` → triggers TTS in Discord (JSON: `{ "text": "...", "channel_id"?, "guild_id"?, "member_id"? }`)

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

| Variable       | Default     | Description                                                                        |
| -------------- | ----------- | ---------------------------------------------------------------------------------- |
| `TTS_ENGINE`   | `gtts`      | Engine to use: `gtts` (Google TTS, best quality) or `pyttsx3` (espeak-ng, offline) |
| `TTS_LANGUAGE` | `pt`        | Language code for gTTS (e.g., `pt`, `en`, `es`, `fr`)                              |
| `TTS_VOICE_ID` | `roa/pt-br` | Voice ID for pyttsx3/espeak-ng (e.g., `roa/pt-br`, `en-us`, `roa/es`)              |

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
- `/config` - Configure your personal TTS settings (with friendly dropdown menus)

### Using `/config` Command

The `/config` command now has **user-friendly dropdown menus** with all available options:

**View your current configuration:**

```
/config
```

**Change your voice settings:**
Simply use `/config` and select from the dropdown options:

- **Voz** (Voice):

  - 🎭 **Mulher do Google** (Google TTS - best quality, requires internet)
  - 🤖 **R.E.P.O.** (Robotic voice - faster, works offline)

- **Idioma** (Language) - for Google voice only:

  - Português, Inglês, Espanhol, Francês, Alemão, Italiano, Japonês, Coreano, Chinês

- **Sotaque** (Accent) - for R.E.P.O. voice only:
  - Português (Brasil), Inglês (EUA), Inglês (Reino Unido), Espanhol, Francês

**Examples:**

- Select "Mulher do Google" + "Inglês" for English Google TTS
- Select "R.E.P.O." + "Português (Brasil)" for Brazilian Portuguese robotic voice

**Note:** Each user has their own voice configuration. Changes you make only affect your voice, not other users. Configuration set via `/config` is temporary and resets when the bot restarts. For permanent default settings, use environment variables on Render.

## Architecture

```
┌─────────────────┐
│  Hotkey App     │  (Windows local)
│  tts_hotkey.py  │  Captures {text} input
└────────┬────────┘
         │ POST /speak
         ▼
┌────────────────┐
│  Discord Bot   │  (Render Docker container)
│  src.bot       │  ← espeak-ng TTS engine
└────────┬───────┘  ← FFmpeg audio processing
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

### ⚠️ Free Tier Limitations (Render):

The **free tier on Render** automatically spins down the service after **15 minutes of inactivity**.

**What happens:**

- Bot goes offline after inactivity
- Discord commands will show "Bot está desligando ou inativo!" with reactivation link
- Service needs manual restart

**How to reactivate:**

1. Access the bot URL: https://python-tts-s3z8.onrender.com/
2. Service will automatically wake up when you access it
3. Bot reconnects to Discord (may take 30-60 seconds)

**Upgrading to paid tier:**

- $7/month removes spin-down behavior
- Bot stays online 24/7
- No manual reactivation needed

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

**Bot not responding or showing "interpreter shutdown" error:**

- Free tier Render service has spun down due to inactivity
- Access the bot URL to wake it up: https://python-tts-s3z8.onrender.com/
- Or use any Discord command - the bot will show the reactivation link
- Wait 30-60 seconds for bot to reconnect to Discord
- Consider upgrading to paid tier for 24/7 availability

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

```bash
# Opção mais simples - instalar dependências e build
make setup && make install && make build-exe

# Ou passo a passo:
./scripts.sh setup
./scripts.sh install
./scripts.sh build-exe
```

**Nota:** Os scripts organizados facilitam o desenvolvimento e build do projeto. Consulte `scripts/README.md` para mais detalhes.

**PowerShell direto (Windows):**

```powershell
# Se encontrar erro de política de execução:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Execute o script (Clean Architecture):
powershell scripts/build/build_clean_architecture.ps1
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
│   ├── core/               # Domain entities & interfaces
│   ├── application/        # Use cases (business logic)
│   ├── infrastructure/     # TTS engines, Discord, HTTP
│   ├── presentation/       # Controllers & commands
│   ├── bot.py             # Main entry point
│   └── app.py             # Application factory
├── config/
│   ├── settings.py        # Configuration
│   └── container.py       # Dependency injection
├── tests/
│   ├── unit/              # Unit tests (77% coverage)
│   └── conftest.py        # Test fixtures
├── Dockerfile             # Docker image with espeak-ng
├── .dockerignore         # Docker build exclusions
├── render.yaml           # Render deployment config
├── wsgi.py              # Gunicorn entry point
├── requirements.txt     # Python dependencies
├── requirements-test.txt # Test dependencies
├── pytest.ini          # Test configuration
├── .env.example       # Environment template
├── README.md         # This file
└── docs/
    └── ARCHITECTURE.md   # Architecture documentation (moved to docs)
```

## Contributing

Fork the repository and submit pull requests for improvements or bug fixes.

## License

This project is licensed under the MIT License.
