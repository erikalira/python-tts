# Environment Setup

This project uses a Python virtual environment (`.venv`) as part of the installation and development flow.

## Requirements

- Python 3.11 or newer
- `uv` 0.11.3 for lockfile-based dependency sync
- `ffmpeg` for the Discord voice flow

## 1. Create `.venv`

From the repository root:

### Windows PowerShell

```powershell
python -m venv .venv
```

### Windows CMD

```cmd
python -m venv .venv
```

### Linux/macOS

```bash
python3 -m venv .venv
```

## 2. Activate `.venv`

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks local scripts, run this permission change once for the current user:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### Windows CMD

```cmd
.\.venv\Scripts\activate.bat
```

### Linux/macOS

```bash
source .venv/bin/activate
```

## 3. Install Dependencies

With `.venv` active:

```bash
python -m pip install uv==0.11.3
uv sync --locked
```

## 4. Install FFmpeg On Windows For Discord Voice

On Windows, the Discord voice flow also needs `FFmpeg` available on `PATH`.

A simple local installation option:

```powershell
winget install ffmpeg
```

After installation, open a new terminal and confirm:

```powershell
ffmpeg -version
```

## 5. Validate The Environment

Check that the terminal is using the virtual environment's Python:

```bash
python --version
pip --version
uv --version
```

The path shown by `pip --version` should point to `.venv`, and `uv --version`
should report the installed `uv` version.

For the Discord bot voice flow, also confirm that `ffmpeg -version` works in the same terminal where the bot will run.

## 5.1. Local Bot Storage

By default, the local bot uses JSON storage:

```env
CONFIG_STORAGE_BACKEND=json
CONFIG_STORAGE_DIR=configs
```

To test the same persistence backend used in production, start only Postgres with Docker:

```bash
docker compose -f docker-compose.postgres.yml up -d
```

Then configure `.env` with:

```env
CONFIG_STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://tts_user:change_me@127.0.0.1:5432/tts_hotkey_windows
POSTGRES_DB=tts_hotkey_windows
POSTGRES_USER=tts_user
POSTGRES_PASSWORD=change_me
POSTGRES_PORT=5432
```

To return to local file storage, stop Postgres if you no longer need it and set `CONFIG_STORAGE_BACKEND=json`.

## 5.2. Optional Redis Queue For The Bot

To use the bot's Redis-backed queue locally, start only Redis with Docker:

```bash
docker compose -f docker-compose.redis.yml up -d
```

Then configure `.env` with:

```env
TTS_QUEUE_BACKEND=redis
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
REDIS_DB=0
REDIS_KEY_PREFIX=tts
REDIS_COMPLETED_ITEM_TTL_SECONDS=900
```

If you do not want Redis, keep `TTS_QUEUE_BACKEND=inmemory`.

## 5.3. Full Local Production Stack

To validate the full stack with bot, Postgres, Redis, and observability, run:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

`docker-compose.prod.yml` also supports bot image versioning through `BOT_IMAGE`
and `APP_VERSION`. In production, publish an image with an immutable tag and
start it with that version recorded in `.env.prod`; to roll back, restore
`APP_VERSION` to the last known good version.

For day-to-day development, prefer starting only the dependencies you need:
`docker-compose.postgres.yml` for Postgres and `docker-compose.redis.yml` for Redis.

## 6. Deactivate When Finished

```bash
deactivate
```

## Notes

- Always activate `.venv` before running `uv sync`, `uv run pytest`, `python -m src.bot`, or `python app.py`.
- On Windows, installing only the Python package is not enough for Discord voice: `FFmpeg` must be installed on the system and available on `PATH`.
- The Discord bot and Desktop App keep separate entrypoints, but they use the same virtual environment during development.
