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
POSTGRES_USER=tts_user
POSTGRES_PASSWORD=change_me_in_production
TTS_ENGINE=gtts
TTS_LANGUAGE=pt
TTS_VOICE_ID=roa/pt-br
TTS_RATE=180
MAX_TEXT_LENGTH=500
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/tts_hotkey_windows
```

For the bundled compose file, keep `POSTGRES_USER`, `POSTGRES_PASSWORD`, and
`DATABASE_URL` in your `.env` file so both services read the same credentials.
The `DATABASE_URL` shown above uses the Docker service name `postgres` as the
host because the bot connects to Postgres from inside the compose network.

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

- Do not keep the default Postgres password. Set `POSTGRES_PASSWORD` in your
  `.env` file and keep it in sync with `DATABASE_URL`.
- Keep `POSTGRES_USER` and `POSTGRES_PASSWORD` in the `.env` file used by
  `docker compose` so the bundled Postgres container and bot container share
  the same credentials.
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
