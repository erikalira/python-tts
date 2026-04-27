# Release Checklist

Use this checklist for production releases that touch runtime behavior, deploy
configuration, dependencies, or shared code used by both applications.

## Release Scope

Record before deploying:

- release owner
- commit SHA and immutable image tag
- affected runtime: bot, desktop, or both
- expected config changes
- migration or restore risk
- rollback point
- staging validation result

For tagged releases, use the `Release` GitHub Actions workflow. It validates the
unit/smoke gates, publishes the bot image to GHCR, and creates release notes
with the published image tag.

## Pre-Release Gates

Run the targeted automated gates from the repository virtual environment.

### Bot

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration tests/smoke/test_release_gates.py -k "bot or release_gates"
```

Required result:

- unit and integration paths are green
- `GET /health` and `GET /observability` contracts remain covered
- queue and runtime observability coverage satisfy `config/quality_gates.json`

### Desktop

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/desktop tests/smoke/test_release_gates.py -k "desktop or release_gates"
```

Required result:

- desktop startup path remains green
- hotkey and tray-owned behavior covered by the changed path remains green
- minimal bot-connected desktop flow remains valid when the change touches
  shared behavior or the HTTP contract

### Shared Safety

Before deploy, confirm:

- no new `src/application/` or `src/presentation/` import points directly to
  `src/infrastructure/`
- bot and desktop entrypoints remain independently runnable
- the `Security` workflow is green for dependency audit, dependency review, and
  CodeQL when applicable
- the `Release` workflow is green when deploying a semantic version tag
- the GHCR image tag in production matches the GitHub release notes
- bot `/speak` rate-limit settings are present in production config or
  intentionally inherited from defaults
- durable docs changed when deploy, runtime, or operational behavior changed
- `.env.prod.example` changed if new production env vars were introduced

### Staging

Before production deploy, run the staging flow in
[../deploy/STAGING_AND_ROLLBACK.md](../deploy/STAGING_AND_ROLLBACK.md).

Required result:

- staging `/health` returns healthy
- staging `/ready` returns ready
- staging live observability gate passes after smoke traffic
- rollback point is recorded

## Deploy

For the bundled Docker production stack:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

If only the bot image changed:

```powershell
docker compose --env-file .env.prod -f docker-compose.prod.yml up -d --no-deps --build bot
```

## Immediate Post-Deploy Checks

Run within the first 5 minutes:

```powershell
Invoke-RestMethod http://127.0.0.1:10000/health
Invoke-RestMethod http://127.0.0.1:10000/observability
docker compose --env-file .env.prod -f docker-compose.prod.yml logs --tail 200 bot
docker compose --env-file .env.prod -f docker-compose.prod.yml ps
```

Pass criteria:

- `GET /health` returns `200` with healthy status
- `GET /observability` returns total request, error-rate, guild, engine, and
  queue-latency fields
- bot logs do not show repeated startup, Redis, Postgres, Discord, or engine
  errors
- bot logs do not show unexpected `RATE_LIMIT` bursts outside intentional load
  or abuse tests
- Docker restart count is stable and the `bot` service health is `healthy`

## Runtime Validation

### Discord Bot

Validate:

- bot process is running
- bot can join or use the expected Discord voice flow
- one short TTS request completes
- queue length returns to zero for the test guild
- error rate does not exceed the release baseline

Useful checks:

```powershell
docker exec tts-hotkey-redis redis-cli smembers "tts:guilds:active"
Invoke-RestMethod http://127.0.0.1:10000/observability
```

### Desktop App

Validate separately from the bot deploy:

- desktop app starts
- configuration window opens and remains editable
- health/status action reaches the bot endpoint when configured
- hotkey path still accepts a short phrase
- tray actions still work

If a headless server cannot validate the desktop app directly, record the
validation gap and run the desktop checks on a Windows workstation before the
release is considered complete.

## Metrics Check

Compare the first post-deploy snapshot against the baseline in
[BASELINE_AND_RELEASE_GATES.md](BASELINE_AND_RELEASE_GATES.md).

Required checks:

- HTTP availability: `GET /health` succeeds
- overall error rate: `<= 5%` during the release window
- queue-to-playback p95: `<= 5000 ms`
- queue-to-playback p99: `<= 15000 ms`
- error rate by engine has no new concentrated failure
- queue age/depth does not keep rising after test traffic stops

If a JSON snapshot was saved, validate it with:

```powershell
.\.venv\Scripts\python.exe scripts/test/quality_gates.py observability --payload path\to\observability.json --config config/quality_gates.json
```

For production, prefer validating the live endpoint after the bot smoke test:

```powershell
.\.venv\Scripts\python.exe scripts/test/quality_gates.py observability --url http://127.0.0.1:10000/observability --config config/quality_gates.json
```

This live SLI gate is expected to run after release smoke traffic has produced
at least one successful playback sample.

When OpenTelemetry is enabled, also check Grafana or Prometheus for:

- `bot.queue.depth`
- `bot.queue.age`
- `bot.queue.lock_loss`
- request and queue processing error counters

## Rollback Criteria

Roll back when any of these remain true after one restart and basic dependency
checks:

- bot health is not stable
- Postgres or Redis connection errors block normal operation
- queue latency keeps rising
- engine error rate is above baseline and fallback does not recover service
- desktop app cannot start after a shared change
- a data migration or config change produced unexpected state

Use [../deploy/STAGING_AND_ROLLBACK.md](../deploy/STAGING_AND_ROLLBACK.md) for
the immediate rollback procedure. Use [DR_DRILLS.md](DR_DRILLS.md) when the
rollback requires database restore or dependency recovery.

## Closeout

Before closing the release:

- capture final health and observability snapshot
- record any validation gap
- record any temporary config or fallback left in place
- create follow-up work for incident residue, flaky checks, missing metrics, or
  manual steps that should become automated
