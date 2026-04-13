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
DATABASE_URL=DATABASE_URL=postgresql://user:password@host:port/tts_hotkey_windows
```

For the bundled compose file, the Postgres connection string is already wired
inside `docker-compose.postgres.yml`, so you only need `DISCORD_TOKEN` unless
you want to override TTS defaults.

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

- Change the default Postgres password in `docker-compose.postgres.yml`.
- Prefer a managed Postgres service in cloud production.
- Keep the bot container stateless and let Postgres hold durable config.
- Back up the Postgres volume or database.
- If the schema already exists, the init SQL is ignored by Postgres container
  bootstrap behavior.

## Manual schema apply

If you are using an external Postgres instead of the bundled container, apply:

- `deploy/postgres/001_bot_config_schema.sql`

Example:

```bash
psql "$DATABASE_URL" -f deploy/postgres/001_bot_config_schema.sql
```
