# python-tts-discord-bot

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/7ed90fe1cc6f4090a7386df4681df463)](https://app.codacy.com?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_coverage)

This repository contains two independent applications:

- A Discord bot that joins voice channels and plays TTS audio
- A Windows Desktop App that captures text with hotkeys and sends it to the bot

The repository follows Clean Architecture and aims to reuse logic between both
runtime flows without duplicating behavior between the Desktop App runtime in
`src/desktop` and the rest of `src`.

## Quick Structure

- `src/bot.py`: starts the Discord bot and HTTP server
- `app.py`: starts the Windows Desktop App
- `src/`: main application layers
- `docs/`: supporting documentation
- `docs/desktop/WINDOWS_BUILD_GUIDE.md`: Windows executable build guide

## Requirements

- Python 3.11+
- `ffmpeg` for the Discord voice flow
- The `.venv` virtual environment is part of the expected setup

Basic installation:

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
winget install ffmpeg
```

### Windows CMD

```cmd
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install -r requirements.txt
winget install ffmpeg
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the complete setup flow, see [docs/getting-started/SETUP.md](docs/getting-started/SETUP.md).

## Quick Start

Create a `.env` file with at least:

```env
DISCORD_TOKEN=your_token_here
DISCORD_BOT_URL=http://127.0.0.1:10000
DISCORD_BOT_PORT=10000
```

To use Redis-backed queues for the local bot:

```bash
docker compose -f docker-compose.redis.yml up -d
```

Then add this to `.env`:

```env
TTS_QUEUE_BACKEND=redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_KEY_PREFIX=tts
REDIS_COMPLETED_ITEM_TTL_SECONDS=900
```

Start the bot:

```bash
python -m src.bot
```

In another terminal, run the Desktop App:

```bash
python app.py
```

## Tests

```bash
pytest
```

Test structure and local execution details live in [docs/getting-started/TESTING.md](docs/getting-started/TESTING.md).

## Windows Executable Build

On Windows, use the official script:

```powershell
./scripts/build/build_clean_architecture.ps1
```

On Linux, build the `.exe` through the CI workflow that runs in a Windows environment.

## Documentation

Use the root README as the entrypoint and keep detailed guidance in the
specific docs. The `docs/` directory is reserved for durable guides; feature
planning and execution artifacts belong in `specs/`.

- [Documentation index](docs/README.md)
- [Environment setup guide](docs/getting-started/SETUP.md)
- [Testing guide](docs/getting-started/TESTING.md)
- [Server deployment guide](docs/deploy/DEPLOYMENT_GUIDE.md)
- [Project architecture](docs/architecture/ARCHITECTURE.md)
- [Desktop App guide](docs/desktop/DESKTOP_APP_GUIDE.md)
- [Canonical constitution and workflow](.specify/README.md)

## Contributor And AI Governance

The canonical architecture, workflow, and agent-instruction rules live in
`.specify/`.

- [Canonical governance index](.specify/README.md)
- [Repository constitution](.specify/memory/constitution.md)
- [Common AI pitfalls](.specify/memory/ai-pitfalls.md)
- [Review checklist](.specify/review-checklist.md)
- [Derivative agent summary](AGENTS.md)

## Notes

- Do not commit `DISCORD_TOKEN`
- The bot and Desktop App must keep working independently
- Prefer `docs/` for architecture, setup, and troubleshooting details
