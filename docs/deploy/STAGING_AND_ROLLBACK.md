# Staging And Rollback

Use this guide when promoting the Docker production stack through staging and
when rolling back a bad release.

## Staging Baseline

Staging should mirror the production stack shape:

- Redis
- Postgres
- bot container
- `/health`
- `/ready`
- `/observability`
- restart policy
- the same schema bootstrap files

Staging does not need production capacity, but it must exercise the same
dependency contracts.

## Staging Environment

Create a staging env file from `.env.prod.example`.

Recommended local name:

```text
.env.staging
```

Use separate values from production:

- separate Discord bot token when possible
- separate Postgres database and password
- separate Redis DB or isolated Redis instance
- staging-specific Grafana credentials

Start staging with the same compose file:

```powershell
docker compose --env-file .env.staging -f docker-compose.prod.yml up -d --build
```

## Staging Promotion Gate

Before production deploy, staging must pass:

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/ready
Invoke-RestMethod http://127.0.0.1:10000/observability
```

After a short bot smoke test produces at least one successful playback sample:

```powershell
.\.venv\Scripts\python.exe scripts/test/quality_gates.py observability --url http://127.0.0.1:10000/observability --config config/quality_gates.json
```

Also confirm:

- Redis and Postgres services are healthy
- bot service is healthy
- the queue drains after the smoke request
- bot logs have no repeated Redis, Postgres, Discord, or engine errors

## Rollback Point

Before deploying production, record:

- current commit SHA or image tag
- target commit SHA or image tag
- env file change summary
- latest Postgres backup path
- rollback owner

Create a pre-release Postgres backup when the release may affect persistence:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/utils/backup_postgres.ps1 `
  -ContainerName tts-bot-postgres `
  -DatabaseName tts_hotkey_windows `
  -DatabaseUser your_postgres_user `
  -BackupDirectory "C:\Backups\tts-bot" `
  -RetentionDays 30
```

## Production Deploy

Deploy the known staging-passed revision:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

If only the bot changed:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --build bot
```

## Rollback

Use rollback when the release breaks health, readiness, queue processing,
storage access, or the desktop-connected bot flow.

1. Restore the previous code revision or image tag.

```powershell
git checkout <known-good-sha-or-tag>
```

2. Restore the previous env file if the incident is configuration-related.

3. Rebuild and restart the bot.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --build bot
```

4. Validate recovery.

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/ready
Invoke-RestMethod http://127.0.0.1:10000/observability
```

5. If persistence was changed and code rollback is insufficient, follow
   [BACKUP_AND_RESTORE_DATABASE.md](BACKUP_AND_RESTORE_DATABASE.md) with the
   selected backup.

## Done Criteria

A deploy or rollback is done only when:

- `/health` returns healthy
- `/ready` returns ready
- the bot service health is `healthy` in Docker
- a short TTS smoke request completes
- the live observability SLI gate passes after smoke traffic
- any validation gap is recorded in the release notes

