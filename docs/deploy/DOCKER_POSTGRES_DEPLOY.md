# Docker + Postgres + Redis Deploy

This guide shows the simplest way to run the Discord bot with Docker,
Postgres, Redis, an OpenTelemetry Collector, Prometheus, Tempo, and Grafana
using the repository files.

## Files involved

- `Dockerfile`
- `docker-compose.prod.yml`
- `docker-compose.postgres.yml`
- `deploy/postgres/001_bot_config_schema.sql`
- `deploy/otel/collector-config.yaml`
- `deploy/observability/tempo.yaml`
- `deploy/observability/prometheus.yml`
- `deploy/observability/prometheus-rules.yml`
- `deploy/observability/grafana/provisioning/datasources/datasources.yaml`
- `deploy/observability/grafana/provisioning/dashboards/dashboards.yaml`
- `deploy/observability/grafana/dashboards/bot-runtime.json`
- `deploy/observability/grafana/dashboards/queue-and-stack.json`

## 1. Prepare environment

Create a production env file based on `.env.prod.example`.

Minimum values:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
BOT_IMAGE=ghcr.io/your-org/tts-hotkey-windows-bot
APP_VERSION=v2026.04.24-1
VCS_REF=<git-sha>
POSTGRES_USER=tts_user
POSTGRES_PASSWORD=change_me_in_production
TTS_ENGINE=gtts
TTS_LANGUAGE=pt
TTS_VOICE_ID=roa/pt-br
TTS_RATE=180
MAX_TEXT_LENGTH=500
POSTGRES_DB=tts_hotkey_windows
POSTGRES_USER=tts_user
POSTGRES_PASSWORD=change_me
TTS_QUEUE_BACKEND=redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_KEY_PREFIX=tts
REDIS_COMPLETED_ITEM_TTL_SECONDS=900
OTEL_ENABLED=true
OTEL_SERVICE_NAME=tts-hotkey-windows-bot
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=change_me
```

For the bundled compose file, the bot `DATABASE_URL` is built inside
`docker-compose.prod.yml` from the same `POSTGRES_*` variables used by the
database container, so you do not need to set `DATABASE_URL` separately.

For the bundled Redis service, use `REDIS_HOST=redis`. Inside Docker, the bot
must connect to the Redis service name, not `127.0.0.1`.

For the bundled OpenTelemetry Collector, use
`OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4318`. Inside Docker, the
bot must connect to the collector service name, not `127.0.0.1`.

Grafana will be available at `http://localhost:3000`, Prometheus at
`http://localhost:9090`, and Tempo at `http://localhost:3200`.

The production compose stack pins dependency images to explicit tags instead of
using `latest`. Update image versions intentionally and validate the stack after
each tag change.

The bot image is versioned separately through `BOT_IMAGE` and `APP_VERSION`.
For production rollback, keep `APP_VERSION` immutable and record the previous
known-good value before every deploy.

## 2. Start the stack

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

If you keep secrets in a different file, replace `.env.prod` with your
real env file.

For a production host that pulls a prebuilt image from a registry, use:

```bash
docker compose --env-file .env.prod -f docker-compose.prod.yml pull bot
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-build
```

## 2.1. Local Postgres only

If you want to run the bot locally from `.venv` but use Postgres instead of JSON
config files, start only the Postgres dependency:

```bash
docker compose -f docker-compose.postgres.yml up -d
```

Then configure `.env` with:

```env
CONFIG_STORAGE_BACKEND=postgres
DATABASE_URL=postgresql://tts_user:change_me@127.0.0.1:5432/tts_hotkey_windows
```

For the simplest local flow, keep `CONFIG_STORAGE_BACKEND=json` and skip
Postgres entirely.

## 3. Check status

```bash
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml logs -f bot
docker compose -f docker-compose.prod.yml logs -f otel-collector
docker compose -f docker-compose.prod.yml logs -f prometheus
docker compose -f docker-compose.prod.yml logs -f tempo
docker compose -f docker-compose.prod.yml logs -f grafana
```

The bot HTTP server will listen on port `10000` by default.
The bundled OpenTelemetry Collector receives OTLP on ports `4317` and `4318`
inside the Docker Compose network. Those ingestion ports are not published on
the host by default.
Grafana will listen on port `3000`.
Prometheus will listen on port `9090`.
Tempo will listen on port `3200` for HTTP queries and Grafana integration. Its
OTLP ingestion ports stay internal to the Docker Compose network.
Prometheus scrapes and evaluates rules every 1 minute by default, and the
bundled Grafana dashboards refresh every 1 minute. This keeps observability
lightweight for the current single-node, solo-operator setup.

## 3. Explore telemetry

1. Open Grafana at `http://localhost:3000`
2. Log in with `GRAFANA_ADMIN_USER` / `GRAFANA_ADMIN_PASSWORD`
3. Open the provisioned `TTS Bot` folder
4. Use the `TTS Bot Runtime` and `TTS Queue and Observability Stack`
   dashboards
5. Use the provisioned `Prometheus` and `Tempo` data sources for ad-hoc
   exploration

The stack is wired like this:

- bot sends OTLP telemetry to `otel-collector`
- collector exports traces to `tempo`
- collector exposes metrics in Prometheus format on `:9464`
- `prometheus` scrapes the collector
- `prometheus` evaluates bundled alerting rules from
  `deploy/observability/prometheus-rules.yml`
- `grafana` queries both Prometheus and Tempo

Prometheus alerts are visible at `http://localhost:9090/alerts`. The bundled
rules cover missing telemetry, target health, queue buildup, queue age,
queue-to-playback latency, high submission error rate, and Redis queue lock
loss. Add Alertmanager or Grafana contact points in the host environment when
you are ready to route these alerts to chat, email, or paging.

## 4. Stop the stack

```bash
docker compose -f docker-compose.prod.yml down
```

To stop and remove the Postgres volume too:

```bash
docker compose -f docker-compose.prod.yml down -v
```

## Notes for real production

- Change `POSTGRES_PASSWORD` in your env file before the first startup.
- Prefer a managed Postgres service in cloud production.
- Prefer a managed Redis service in cloud production when available.
- Keep the bot container stateless and let Postgres hold durable config.
- Back up the Postgres volume or database.
- If the schema already exists, the init SQL is ignored by Postgres container
  bootstrap behavior.
- The bundled stack now stores traces in Tempo local storage and metrics in
  Prometheus TSDB volumes, which is fine for a single-node deployment but not
  a substitute for a HA observability platform.
- The current pinned image tags are intentionally conservative and should be
  reviewed as part of dependency maintenance.

## Credential change note

The official Postgres container only applies `POSTGRES_USER`,
`POSTGRES_PASSWORD`, and `POSTGRES_DB` while initializing a new data
directory. If you change those values after the `postgres_data` volume already
exists, the container keeps the old database credentials.

When that happens, the bot can fail with `password authentication failed` even
though your current env file looks correct.

Recovery options:

1. If you do not need the existing database contents, recreate the volume:

```bash
docker compose -f docker-compose.prod.yml down -v
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
```

2. If you need to keep the data, update the password inside Postgres instead
   of recreating the volume:

```bash
docker exec -it tts-bot-postgres psql -U CURRENT_DB_USER -d tts_hotkey_windows
ALTER USER CURRENT_DB_USER WITH PASSWORD 'NEW_PASSWORD';
```

## Manual schema apply

If you are using an external Postgres instead of the bundled container, apply:

- `deploy/postgres/001_bot_config_schema.sql`

Example:

```bash
psql "$DATABASE_URL" -f deploy/postgres/001_bot_config_schema.sql
```
