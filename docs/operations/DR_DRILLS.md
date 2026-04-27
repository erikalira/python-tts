# Disaster Recovery Drills

These drills verify that production can recover from dependency loss and bad
deploys without improvising during an incident.

Run the drills in a staging environment first. Production drills should use a
planned window, explicit owner, and written rollback point.

## Drill Cadence

| Drill | Recommended cadence |
| --- | --- |
| Postgres restore | monthly until boring, then quarterly |
| Redis recovery | quarterly or after queue architecture changes |
| Version rollback | every release train or after deployment flow changes |

## Shared Rules

- Do not start a destructive restore without naming the exact backup file or
  version tag.
- Keep a timestamped incident/drill note with command output summaries.
- Validate `GET /health` and `GET /observability` after every recovery.
- Validate the Discord bot and Windows desktop app separately when a release or
  rollback may affect shared behavior.
- Prefer restoring into staging before touching production.

## Postgres Restore Drill

Postgres stores durable bot configuration. The detailed backup and restore
script usage lives in [../deploy/BACKUP_AND_RESTORE_DATABASE.md](../deploy/BACKUP_AND_RESTORE_DATABASE.md).

### Preconditions

- A recent `.dump` file exists outside the container.
- The operator knows the expected `POSTGRES_DB`, `POSTGRES_USER`, and container
  name.
- The current database state has been backed up before the drill.

### Staging Drill

1. Start the stack.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d postgres bot
```

2. Confirm the bot can read config storage.

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail 100 bot
```

3. Restore the selected dump.

```powershell
powershell -ExecutionPolicy Bypass -File scripts/utils/restore_postgres.ps1 `
  -BackupFile "C:\Backups\tts-bot\tts_backup_YYYY-MM-DD_HH-mm-ss.dump" `
  -ContainerName tts-bot-postgres `
  -DatabaseName tts_hotkey_windows `
  -DatabaseUser your_postgres_user
```

4. Restart the bot.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml restart bot
```

5. Validate recovery.

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/observability
```

6. Confirm representative guild or user TTS settings still resolve.

### Success Criteria

- Restore completes without `pg_restore` errors.
- Bot health returns to `200`.
- Bot logs have no Postgres authentication or schema errors.
- Known TTS settings are present after restore.
- Recovery time is recorded.

### Production Notes

For a real production restore:

1. announce the maintenance window
2. pause deploys
3. create a final pre-restore backup
4. restore the selected known-good dump
5. restart bot
6. validate health, logs, settings, and a short TTS flow

## Redis Recovery Drill

Redis is used for queue coordination and transient queue state. Postgres remains
the durable source for bot configuration. In many incidents, the safest Redis
recovery is to clear or recreate transient queue state and let users retry.

### Recovery Choice

| Situation | Preferred recovery |
| --- | --- |
| Redis process crashed and restarts cleanly | let Docker restart it, then validate |
| Redis data is corrupt or queues are unrecoverable | recreate Redis volume during a window |
| A single guild queue is bad | clear only that guild queue keys |
| You must preserve queued items | restore from Redis AOF/RDB snapshot, then validate carefully |

The bundled compose stack starts Redis with append-only file persistence:

```yaml
command: ["redis-server", "--appendonly", "yes"]
```

That improves restart survivability, but it is not a substitute for a tested
business backup strategy.

### Non-Destructive Drill

1. Confirm Redis responds.

```powershell
docker exec tts-hotkey-redis redis-cli ping
docker exec tts-hotkey-redis redis-cli info persistence
```

2. Restart Redis and bot.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml restart redis
docker compose --env-file .env.prod -f docker-compose.prod.yml restart bot
```

3. Validate.

```powershell
docker exec tts-hotkey-redis redis-cli ping
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/observability
```

4. Submit a short TTS request and verify playback.

### Recreate Drill

Use only in staging or a production maintenance window. This removes transient
queue state.

1. Stop bot and Redis.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml stop bot redis
```

2. Remove only the Redis volume.

```powershell
docker volume rm tts-hotkey-windows_redis_data
```

3. Start Redis and bot.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d redis bot
```

4. Validate health and a short TTS flow.

### Success Criteria

- Redis answers `PONG`.
- Bot reconnects without manual code changes.
- New queue items can be enqueued and drained.
- Operators can explain whether queued work was preserved or discarded.

## Version Rollback Drill

Rollback proves that a bad bot image or environment change can be reversed.

### Preconditions

- The last known-good commit SHA or image tag is known.
- The current `.env.prod` is backed up.
- Postgres backup exists before the drill.
- The operator knows whether the deployment uses source checkout, built image,
  or both.

### Image-Based Rollback

Use this path when production deploys GHCR images built by the `Release`
workflow.

1. Open the `Rollback Bot Image` workflow.
2. Keep `dry_run=true` and enter the previous known-good image tag.
3. Confirm the generated commands target the expected compose and env files.
4. Re-run with `dry_run=false` from a runner that can reach the Docker host.
5. Validate health, readiness, observability, logs, and one short TTS flow.

Success means the bot service is recreated from the previous immutable image
tag without rebuilding from source.

### Source-Based Rollback

1. Record the current commit.

```powershell
git rev-parse HEAD
```

2. Check out the last known-good version.

```powershell
git fetch --all --tags
git checkout <known-good-sha-or-tag>
```

3. Rebuild and restart only the bot.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --build bot
```

4. Validate.

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/observability
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail 200 bot
```

5. Run a short Discord TTS smoke test.

### Environment Rollback

Use this when the code is good but a config change caused the incident.

1. Restore the previous `.env.prod`.
2. Recreate the bot container.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps bot
```

3. Validate health, observability, and a short TTS flow.

### Success Criteria

- Rollback completes in the target recovery window.
- Bot health returns to `200`.
- No Postgres or Redis credentials drift remains.
- Queue latency and error rate return below the release baseline.
- The rollback point and reason are recorded.

