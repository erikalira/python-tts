# Environment Configuration

This project has two independent runtimes with different environment needs:

- Discord bot deployed in the cloud, whether public or private
- Windows Desktop App running locally

Use the examples in the repository root as the starting point:

- `.env.example`: local development defaults
- `.env.prod.example`: Dockerized bot + Postgres + Redis example for the bundled compose stack

## Environment Summary

| Variable | Local `.env` | Cloud bot service | Required | Notes |
| --- | --- | --- | --- | --- |
| `DISCORD_TOKEN` | Yes | Yes | Yes for bot | Required by the Discord bot runtime. |
| `BOT_IMAGE` | Optional | Docker Compose only | Recommended for production Compose | Bot image repository/name used by `docker-compose.prod.yml`. Use a registry path in production. |
| `APP_VERSION` | Optional | Docker Compose only | Recommended for production Compose | Immutable application version tag for the bot image. Rollbacks should return to a known-good value. |
| `VCS_REF` | Optional | Docker Compose only | Recommended for production Compose | Git SHA/revision recorded as image metadata when building. |
| `DISCORD_BOT_URL` | Yes | No | No | Used by the Desktop App to reach the bot API. |
| `DISCORD_BOT_PORT` | Optional | Usually no | No | Local fallback when `PORT` is absent. |
| `PORT` | No | Usually yes | Recommended in cloud deploys | Many platforms provide this automatically. |
| `DISCORD_BOT_HOST` | Optional | Yes | Yes in cloud practice | Use `0.0.0.0` in deploys so the HTTP server is reachable. |
| `BOT_HTTP_CORS_ALLOWED_ORIGINS` | Optional | Optional | No | Comma-separated browser origin allowlist for bot HTTP endpoints. Empty means no browser origins are allowed. Do not use `*`. |
| `BOT_SPEAK_TOKEN` | Optional | Yes when non-loopback | Required when `DISCORD_BOT_HOST` is not loopback | Shared token for `POST /speak`. Desktop sends it through `X-Bot-Token` when configured. Store as a secret and never commit real values. |
| `BOT_HTTP_MAX_BODY_BYTES` | Optional | Optional | No | Maximum accepted HTTP request body size in bytes. Defaults to `4096`. |
| `DISCORD_MEMBER_ID` | Optional | No | No | Desktop App targeting preference. |
| `BOT_RATE_LIMIT_MAX_REQUESTS` | Optional | Optional | No | Maximum `/speak` requests per caller within the configured window. Defaults to `8`; use `0` to disable. |
| `BOT_RATE_LIMIT_WINDOW_SECONDS` | Optional | Optional | No | Sliding rate-limit window for bot `/speak` entrypoints. Defaults to `10`. |
| `TTS_ENGINE` | Optional | Optional | No | Defaults to `gtts`. Validated by the bot runtime. Accepted values today: `gtts`, `pyttsx3`, `edge-tts`. |
| `TTS_LANGUAGE` | Optional | Optional | No | Defaults to `pt`. |
| `TTS_VOICE_ID` | Optional | Optional | No | Defaults to `roa/pt-br`. |
| `TTS_RATE` | Optional | Optional | No | Defaults to `180`. |
| `TTS_OUTPUT_DEVICE` | Optional | No | No | Desktop-only local audio output setting. |
| `MAX_TEXT_LENGTH` | Optional | Optional | No | Bot runtime limit for incoming text. |
| `CONFIG_STORAGE_BACKEND` | Optional | Yes | Yes in practice for production | `json` for local dev, `postgres` for production-grade bot persistence. |
| `CONFIG_STORAGE_DIR` | Optional | No | No | Directory used only by the JSON config backend. |
| `DATABASE_URL` | Optional | Yes | Required with `CONFIG_STORAGE_BACKEND=postgres` | Postgres connection string for durable bot configuration. For local `docker-compose.postgres.yml`, use `postgresql://tts_user:change_me@127.0.0.1:5432/tts_hotkey_windows`. |
| `POSTGRES_DB` | Optional | Docker Compose only | Required in practice for bundled Postgres | Compose database name for the repository's bundled Postgres container. |
| `POSTGRES_USER` | Optional | Docker Compose only | Required in practice for bundled Postgres | Compose credential used by the repository's bundled Postgres container. Keep it aligned with `DATABASE_URL`. |
| `POSTGRES_PASSWORD` | Optional | Docker Compose only | Required in practice for bundled Postgres | Compose password used by the repository's bundled Postgres container. Keep it aligned with `DATABASE_URL`. |
| `POSTGRES_PORT` | Optional | No | No | Host port used only by `docker-compose.postgres.yml`. Defaults to `5432`. |
| `TTS_QUEUE_BACKEND` | Optional | Optional | No | `inmemory` for local simplicity, `redis` for a Dockerized durable queue backend. |
| `REDIS_HOST` | Optional | Optional | Required with `TTS_QUEUE_BACKEND=redis` | Use `127.0.0.1` when the bot runs locally and Redis is published to the host; use `redis` when the bot runs inside the bundled compose stack. |
| `REDIS_PORT` | Optional | Optional | Required with `TTS_QUEUE_BACKEND=redis` | Redis port. Defaults to `6379`. |
| `REDIS_DB` | Optional | Optional | No | Redis logical database. Defaults to `0`. |
| `REDIS_KEY_PREFIX` | Optional | Optional | No | Prefix for bot queue keys. Defaults to `tts`. |
| `REDIS_COMPLETED_ITEM_TTL_SECONDS` | Optional | Optional | No | Retention for completed queue items in Redis. Defaults to `900`. |
| `OTEL_ENABLED` | Optional | Optional | No | Enables manual OpenTelemetry tracing and metrics when set to `true` and an OTLP endpoint is configured. |
| `OTEL_SERVICE_NAME` | Optional | Optional | No | OpenTelemetry service name. Defaults to `tts-hotkey-windows-bot`. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | Optional | Optional | Required when `OTEL_ENABLED=true` | Base OTLP HTTP collector endpoint, for example `http://collector:4318`. |
| `GRAFANA_ADMIN_USER` | No | Docker Compose only | No | Admin username for the bundled Grafana instance. Defaults to `admin`. |
| `GRAFANA_ADMIN_PASSWORD` | No | Docker Compose only | Recommended with bundled Grafana | Admin password for the bundled Grafana instance. |

## Local Development

For local development, create `.env` from `.env.example`.

Recommended minimum values:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
DISCORD_BOT_URL=http://localhost:10000
DISCORD_BOT_PORT=10000
# Optional locally; set it in both bot and Desktop App environments when used.
BOT_SPEAK_TOKEN=
BOT_HTTP_MAX_BODY_BYTES=4096
```

Notes:

- `DISCORD_BOT_URL` is primarily for the Desktop App.
- `DISCORD_BOT_PORT` is used as the bot HTTP port when `PORT` is not set.
- `DISCORD_MEMBER_ID` is the only Desktop App identifier still needed for Discord voice-context detection.
- `CONFIG_STORAGE_BACKEND=json` remains the simplest local default.
- To test Postgres locally without the full production stack, run
  `docker compose -f docker-compose.postgres.yml up -d` and set
  `CONFIG_STORAGE_BACKEND=postgres`.

## Cloud Production

For a cloud-hosted bot that connects to an external Postgres instance, provide
the runtime values directly.

Recommended minimum values:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
DISCORD_BOT_HOST=0.0.0.0
BOT_SPEAK_TOKEN=change_me_in_production
BOT_HTTP_MAX_BODY_BYTES=4096
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

## Bundled Docker + Postgres + Redis Stack

For `docker-compose.prod.yml`, use `.env.prod.example` as the starting
point.

Recommended minimum values:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
BOT_IMAGE=ghcr.io/your-org/tts-hotkey-windows-bot
APP_VERSION=v2026.04.24-1
VCS_REF=<git-sha>
CONFIG_STORAGE_BACKEND=postgres
POSTGRES_DB=tts_hotkey_windows
POSTGRES_USER=tts_user
POSTGRES_PASSWORD=change_me
TTS_QUEUE_BACKEND=redis
REDIS_HOST=redis
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=change_me
```

Notes:

- `APP_VERSION` should be an immutable release tag, not `latest`. Rollback is
  done by restoring the previous known-good `APP_VERSION` and restarting the
  bot without rebuilding.
- The bundled compose stack builds `DATABASE_URL` for the bot from
  `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`.
- The bundled compose stack includes Redis. Use `REDIS_HOST=redis` so the bot
  container connects through Docker service discovery.
- For OpenTelemetry, set `OTEL_ENABLED=true` and point
  `OTEL_EXPORTER_OTLP_ENDPOINT` to an OTLP HTTP collector such as
  `http://otel-collector:4318`.
- The bundled compose stack also includes Grafana, Prometheus, and Tempo for a
  self-hosted OSS observability path.
- With the bundled stack, do not maintain a second manual `DATABASE_URL` unless
  you are intentionally pointing the bot at a different database service.
- Docker images in the compose files are pinned to explicit tags. Update those
  tags intentionally through the dependency maintenance workflow instead of
  switching back to `latest`.

## Local Postgres Only

Use `docker-compose.postgres.yml` when you want local Postgres persistence but
still want to run the bot from the Python virtual environment.

```powershell
docker compose -f docker-compose.postgres.yml up -d
```

Then set:

```env
CONFIG_STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://tts_user:change_me@127.0.0.1:5432/tts_hotkey_windows
```

To return to file-backed local storage:

```env
CONFIG_STORAGE_BACKEND=json
CONFIG_STORAGE_DIR=configs
```

## Runtime Sources

The current bot runtime reads its environment from [`src/bot_runtime/settings.py`](../../src/bot_runtime/settings.py).

The Desktop App local defaults are derived from [`src/desktop/config/models.py`](../../src/desktop/config/models.py) and [`src/desktop/config/repository.py`](../../src/desktop/config/repository.py).
