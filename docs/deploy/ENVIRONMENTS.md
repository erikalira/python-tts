# Environment Configuration

This project has two independent runtimes with different environment needs:

- Discord bot deployed in the cloud, whether public or private
- Windows Desktop App running locally

Use the examples in the repository root as the starting point:

- `.env.example`: local development defaults
- `.env.prod.example`: production example for the bot in cloud deploys

## Environment Summary

| Variable | Local `.env` | Cloud bot service | Required | Notes |
| --- | --- | --- | --- | --- |
| `DISCORD_TOKEN` | Yes | Yes | Yes for bot | Required by the Discord bot runtime. |
| `DISCORD_BOT_URL` | Yes | No | No | Used by the Desktop App to reach the bot API. |
| `DISCORD_BOT_PORT` | Optional | Usually no | No | Local fallback when `PORT` is absent. |
| `PORT` | No | Usually yes | Recommended in cloud deploys | Many platforms provide this automatically. |
| `DISCORD_BOT_HOST` | Optional | Yes | Yes in cloud practice | Use `0.0.0.0` in deploys so the HTTP server is reachable. |
| `DISCORD_MEMBER_ID` | Optional | No | No | Desktop App targeting preference. |
| `TTS_ENGINE` | Optional | Optional | No | Defaults to `gtts`. Validated by the bot runtime. Accepted values today: `gtts`, `pyttsx3`, `edge-tts`. |
| `TTS_LANGUAGE` | Optional | Optional | No | Defaults to `pt`. |
| `TTS_VOICE_ID` | Optional | Optional | No | Defaults to `roa/pt-br`. |
| `TTS_RATE` | Optional | Optional | No | Defaults to `180`. |
| `TTS_OUTPUT_DEVICE` | Optional | No | No | Desktop-only local audio output setting. |
| `MAX_TEXT_LENGTH` | Optional | Optional | No | Bot runtime limit for incoming text. |
| `CONFIG_STORAGE_BACKEND` | Optional | Yes | Yes in practice for production | `json` for local dev, `postgres` for production-grade bot persistence. |
| `CONFIG_STORAGE_DIR` | Optional | No | No | Directory used only by the JSON config backend. |
| `DATABASE_URL` | No | Yes | Required with `CONFIG_STORAGE_BACKEND=postgres` | Postgres connection string for durable bot configuration. |
| `POSTGRES_USER` | No | Docker Compose only | Required in practice for bundled Postgres | Compose credential used by the repository's bundled Postgres container. Keep it aligned with `DATABASE_URL`. |
| `POSTGRES_PASSWORD` | No | Docker Compose only | Required in practice for bundled Postgres | Compose password used by the repository's bundled Postgres container. Keep it aligned with `DATABASE_URL`. |

## Local Development

For local development, create `.env` from `.env.example`.

Recommended minimum values:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
DISCORD_BOT_URL=http://localhost:10000
DISCORD_BOT_PORT=10000
```

Notes:

- `DISCORD_BOT_URL` is primarily for the Desktop App.
- `DISCORD_BOT_PORT` is used as the bot HTTP port when `PORT` is not set.
- `DISCORD_MEMBER_ID` is the only Desktop App identifier still needed for Discord voice-context detection.
- `CONFIG_STORAGE_BACKEND=json` remains the simplest local default.

## Cloud Production

For the bot deployed in the cloud, use `.env.prod.example` as the reference.

Recommended minimum values:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
DISCORD_BOT_HOST=0.0.0.0
POSTGRES_USER=tts_user
POSTGRES_PASSWORD=change_me_in_production
CONFIG_STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/tts_hotkey_windows
```

Notes:

- In this repository, the runtime prioritizes `PORT` over `DISCORD_BOT_PORT`.
- Many cloud platforms expose the listening port through `PORT`. In this repository, `render.yaml` sets it to `10000` for that specific platform.
- `DISCORD_BOT_PORT` is not usually needed in cloud deploys when `PORT` is already provided.
- `DISCORD_BOT_URL` is not needed in cloud deploys for the bot service itself.
- `DATABASE_URL` becomes mandatory when the bot uses `CONFIG_STORAGE_BACKEND=postgres`.
- When using the repository's bundled Docker Compose Postgres, keep
  `POSTGRES_USER` and `POSTGRES_PASSWORD` in the same `.env` file and match
  them with the credentials embedded in `DATABASE_URL`.

## Runtime Sources

The current bot runtime reads its environment from [`src/bot_runtime/settings.py`](../../src/bot_runtime/settings.py).

The Desktop App local defaults are derived from [`src/desktop/config/models.py`](../../src/desktop/config/models.py) and [`src/desktop/config/repository.py`](../../src/desktop/config/repository.py).
