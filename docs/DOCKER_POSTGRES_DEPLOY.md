# Docker + Postgres Deploy

This guide shows the simplest way to run the Discord bot with Docker and
Postgres using the repository files.

## Files involved

- `Dockerfile`
- `docker-compose.postgres.yml`
- `deploy/postgres/001_bot_config_schema.sql`

## 1. Prepare environment

Create a production env file based on `.env.prod.example`.

Minimum values:

```env
DISCORD_TOKEN=YOUR_DISCORD_BOT_TOKEN
TTS_ENGINE=gtts
TTS_LANGUAGE=pt
TTS_VOICE_ID=roa/pt-br
TTS_RATE=180
MAX_TEXT_LENGTH=500
POSTGRES_DB=tts_hotkey_windows
POSTGRES_USER=tts_user
POSTGRES_PASSWORD=change_me
```

For the bundled compose file, the bot `DATABASE_URL` is built inside
`docker-compose.postgres.yml` from the same `POSTGRES_*` variables used by the
database container, so you do not need to set `DATABASE_URL` separately.

## 2. Start the stack

```bash
docker compose --env-file .env.prod.example -f docker-compose.postgres.yml up -d --build
```

If you keep secrets in a different file, replace `.env.prod.example` with your
real env file.

## 3. Check status

```bash
docker compose -f docker-compose.postgres.yml ps
docker compose -f docker-compose.postgres.yml logs -f bot
```

The bot HTTP server will listen on port `10000` by default.

## 4. Stop the stack

```bash
docker compose -f docker-compose.postgres.yml down
```

To stop and remove the Postgres volume too:

```bash
docker compose -f docker-compose.postgres.yml down -v
```

## Notes for real production

- Change `POSTGRES_PASSWORD` in your env file before the first startup.
- Prefer a managed Postgres service in cloud production.
- Keep the bot container stateless and let Postgres hold durable config.
- Back up the Postgres volume or database.
- If the schema already exists, the init SQL is ignored by Postgres container
  bootstrap behavior.

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
docker compose -f docker-compose.postgres.yml down -v
docker compose --env-file .env.prod -f docker-compose.postgres.yml up -d --build
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
