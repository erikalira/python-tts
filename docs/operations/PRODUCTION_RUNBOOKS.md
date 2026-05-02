# Production Runbooks

Runbooks for the production Docker stack:

- Redis
- Postgres
- Discord bot
- healthcheck and restart policy
- optional OpenTelemetry, Prometheus, Tempo, and Grafana services
- optional Alertmanager routing to a Discord incident channel

Use these procedures during incidents. Keep notes with timestamps, commands
run, observed values, and the final recovery action.

## First Response

1. Confirm the incident scope.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail 200 bot
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail 100 redis
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail 100 postgres
```

2. Check bot readiness and in-memory observability.

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/observability
```

3. Classify the failure.

| Symptom | Most likely class |
| --- | --- |
| `GET /health` fails or times out | bot down, startup failure, dependency unavailable |
| queue age or p95/p99 rises while health is `200` | queue stuck, engine degradation, voice runtime issue |
| Redis logs show restarts or connection failures | Redis dependency issue |
| Postgres auth or connection errors in bot logs | config storage issue |
| one engine bucket has high errors | engine degradation |
| Discord incident channel receives a critical alert | follow the matching runbook and acknowledge in the incident thread |

4. Prefer the smallest reversible recovery first.

- Restart only `bot` when Redis and Postgres are healthy.
- Restart `redis` only when Redis itself is unhealthy or corrupted.
- Restore Postgres only when data is missing or wrong and a backup was
  selected.
- Roll back only when the current version is plausibly the cause.

## Alertmanager Incident Routing

Alertmanager receives Prometheus alerts and posts warning and critical
notifications to the configured Discord webhook.

### Signals

- A Discord incident message arrives with `FIRING`.
- `http://localhost:9090/alerts` shows the alert as firing.
- `http://localhost:9093` shows the alert grouped under the Discord receiver.

### Triage

1. Acknowledge the incident in the Discord thread with the current owner and
   timestamp.
2. Open Prometheus and identify the alert name, severity, job, and instance.
3. Follow the matching runbook section for lock starvation, stuck queue, engine
   degradation, dependency outage, or rollback.
4. When the alert resolves, confirm Discord receives the resolved notification.

### Follow-Up

Record false positives, missing routing, repeated notifications, or alerts
that did not resolve. Tune `deploy/observability/prometheus-rules.yml` or
`deploy/observability/alertmanager.yml` in Git rather than changing live
configuration by hand.

## Lock Starvation

Lock starvation means queued work exists, but a guild lock or processing lease
keeps new processing from making progress.

### Signals

- `GET /health` returns `200`.
- Users keep receiving queued responses, but playback does not progress.
- `GET /observability` shows rising `enqueue_to_playback_p95_ms` or
  `enqueue_to_playback_p99_ms`.
- Bot logs contain repeated queue worker messages about busy locks, lost locks,
  lost processing leases, or guild drain failures.
- Redis contains lock or processing keys that outlive active work.

### Inspect

Use the configured `REDIS_KEY_PREFIX`. The production default is `tts`.

```powershell
docker exec tts-hotkey-redis redis-cli keys "tts:*guild*"
docker exec tts-hotkey-redis redis-cli keys "tts:lock:guild:*"
docker exec tts-hotkey-redis redis-cli keys "tts:processing:guild:*"
docker exec tts-hotkey-redis redis-cli ttl "tts:lock:guild:<guild-id>"
docker exec tts-hotkey-redis redis-cli ttl "tts:processing:guild:<guild-id>"
```

Expected behavior:

- lock and processing keys should have a positive TTL while active work exists
- stale lock keys should expire after `QUEUE_GUILD_LOCK_TTL_SECONDS`
- stale processing keys should expire after
  `QUEUE_PROCESSING_LEASE_TTL_SECONDS`

### Contain

1. Restart the bot to stop the current worker and release in-process work.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml restart bot
```

2. Recheck health and observability after the bot starts.

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/observability
```

3. If a single guild is still blocked and a stale key has an abnormal TTL,
delete only that stale lock or processing key.

```powershell
docker exec tts-hotkey-redis redis-cli del "tts:lock:guild:<guild-id>"
docker exec tts-hotkey-redis redis-cli del "tts:processing:guild:<guild-id>"
```

Do not delete queue or item keys during lock recovery unless the incident is
being handled as a stuck queue.

### Recover

After recovery, confirm:

- the bot stays healthy for at least 5 minutes
- the queue p95/p99 stops rising
- no new lock-loss loop appears in bot logs
- users can submit and hear a short test phrase

### Follow-Up

Open a ticket if any of these are true:

- lock starvation repeats in the same day
- a lock key has no TTL
- a processing lease survives a bot restart beyond its configured TTL
- queue latency returns to normal only after manual Redis key deletion

Include the Redis key names, TTL values, bot logs, and `/observability` payload.

## Stuck Queue

A stuck queue means pending items are present, but the queue is not draining.
This can be caused by a worker failure, voice connection problem, Redis issue,
or a bad item.

### Signals

- `GET /health` is healthy while queue latency rises.
- Users repeatedly receive queued responses.
- `bot.queue.age` grows in metrics when OpenTelemetry is enabled.
- Redis queue list length is non-zero for one or more guilds.

### Inspect

```powershell
docker exec tts-hotkey-redis redis-cli smembers "tts:guilds:active"
docker exec tts-hotkey-redis redis-cli llen "tts:queue:guild:<guild-id>"
docker exec tts-hotkey-redis redis-cli lrange "tts:queue:guild:<guild-id>" 0 10
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail 300 bot
```

For one queued item:

```powershell
docker exec tts-hotkey-redis redis-cli get "tts:item:<item-id>"
```

Look for:

- an item that repeatedly fails generation or playback
- queue length that never decreases
- `queue_worker` exceptions
- Discord voice errors
- TTS generation or playback timeout codes

### Contain

1. Restart only the bot if Redis is healthy.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml restart bot
```

2. If the queue is blocked by one bad item, preserve the item payload in the
   incident notes and remove that item from the queue list.

```powershell
docker exec tts-hotkey-redis redis-cli lrem "tts:queue:guild:<guild-id>" 1 "<item-id>"
```

3. If the whole guild queue is no longer valuable and users can retry, clear
   only that guild queue and its active processing markers.

```powershell
docker exec tts-hotkey-redis redis-cli del "tts:queue:guild:<guild-id>"
docker exec tts-hotkey-redis redis-cli del "tts:lock:guild:<guild-id>"
docker exec tts-hotkey-redis redis-cli del "tts:processing:guild:<guild-id>"
```

Avoid `flushall` in production. It removes every Redis key, including other
guild queues and operational state.

### Recover

1. Submit a short TTS request in the affected guild.
2. Confirm playback completes.
3. Confirm queue length returns to zero.

```powershell
docker exec tts-hotkey-redis redis-cli llen "tts:queue:guild:<guild-id>"
Invoke-RestMethod http://127.0.0.1:10000/observability
```

### Follow-Up

Capture:

- item payload if a single item caused the block
- engine used by the item
- text length
- timeout or playback error
- whether the item should become a regression test

## Engine Degradation

Engine degradation means one TTS engine fails, slows down, or times out while
the bot and queue worker are otherwise alive.

### Signals

- `/observability` shows elevated `error_rate_by_engine`.
- Queue p95/p99 rises while queue length keeps changing.
- Logs contain `generation_timeout`, `playback_timeout`, or engine exceptions.
- Users report delayed or missing playback, but bot commands still respond.

### Inspect

```powershell
Invoke-RestMethod http://127.0.0.1:10000/observability
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail 300 bot
```

Check the configured default engine:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml exec bot printenv TTS_ENGINE
docker compose --env-file .env.prod -f docker-compose.prod.yml exec bot printenv TTS_VOICE_ID
```

Supported bot engines are configured through the normal TTS config path. The
current code accepts `gtts`, `pyttsx3`, and `edge-tts`; production Docker
deploys should prefer an engine that is known to work in the container runtime.

### Contain

1. If only one engine is degraded, switch the default engine in `.env.prod` to
   the approved fallback for this deployment.

```env
TTS_ENGINE=gtts
TTS_LANGUAGE=pt
TTS_VOICE_ID=roa/pt-br
```

2. Recreate the bot container with the updated environment.

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --build bot
```

3. Temporarily reduce request pressure if needed.

```env
MAX_TEXT_LENGTH=300
```

### Recover

Confirm:

- a short phrase plays successfully
- engine-specific error rate stops rising
- queue p95/p99 returns below the release-gate baseline
- bot logs do not show repeated generation or playback timeouts

### Follow-Up

Record the degraded engine, external dependency status, error codes, and the
fallback used. If the fallback must stay longer than one release window, update
the deploy notes so the temporary state is visible.

