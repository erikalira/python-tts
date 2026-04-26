# Baseline And Release Gates

This guide defines the Phase 0 operational baseline for the Discord bot and
the Windows desktop app.

## Success Criteria

- The bot must expose `GET /health` and respond with HTTP `200`.
- The bot must expose `GET /observability` and report:
  - total request volume
  - overall error rate
  - error rate by guild
  - error rate by engine
  - `enqueue -> playback` latency p95/p99 based on successful playbacks
- The desktop app must still start and complete a minimal bot-connected flow.
- Both application modes must remain independently runnable.

## Initial SLI And SLO Baseline

These targets are the initial baseline, not a long-term contract. They are
meant to make the current system measurable before deeper optimization work.

- Bot HTTP availability SLI: successful responses from `GET /health`.
- Bot HTTP availability initial SLO: `>= 99.0%` over the chosen release window.
- Queue-to-playback latency SLI: p95 and p99 from `GET /observability`,
  measured from `AudioQueueItem.created_at` to successful playback completion.
- Queue-to-playback initial SLO: p95 `<= 5000 ms`; p99 `<= 15000 ms`.
- Error-rate SLI: `failed_requests / total_requests`, plus the same breakdown by
  guild and engine from `GET /observability`.
- Error-rate initial SLO: overall error rate `<= 5%` for normal releases.
- Prometheus runtime metrics mirror the operational baseline when
  `OTEL_ENABLED=true`:
  - `bot_tts_submissions_total`
  - `bot_tts_enqueue_to_playback_seconds_bucket`
  - `bot_queue_items_processed_total`
  - `bot_queue_depth_*`
  - `bot_queue_age_seconds_bucket`
  - `bot_queue_lock_loss_total`

## Release Gates

Repository thresholds are centralized in `config/quality_gates.json` so CI,
local runs, and smoke checks enforce the same baseline.

### Discord bot

- Required automated gate:
  `.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration tests/smoke/test_release_gates.py -k "bot or release_gates"`
- Minimum expectation:
  unit coverage stays green, critical integration paths stay green, and the
  bot health/observability endpoints remain available.
- Coverage gate:
  global covered lines must stay at or above `80%`.
- Critical domain gates:
  - `queue`: `src/application/tts_queue_orchestrator.py`,
    `src/infrastructure/audio_queue.py`, and
    `src/bot_runtime/queue_worker.py` aggregated at `>= 80%`
  - `runtime_observability`: `src/application/runtime_telemetry.py` and
    `src/infrastructure/runtime_observability.py` aggregated at `>= 95%`
- SLI regression gate:
  smoke checks fail if the baseline payload regresses past the configured
  `error_rate`, `enqueue_to_playback_p95_ms`, or
  `enqueue_to_playback_p99_ms` thresholds.

### Desktop app

- Required automated gate:
  `.\.venv\Scripts\python.exe -m pytest tests/unit/desktop tests/smoke/test_release_gates.py -k "desktop or release_gates"`
- Minimum expectation:
  startup still succeeds, hotkey/tray services can start, and the minimal bot
  interaction flow still works.

## Notes

- To validate coverage gates from a generated `coverage.xml`, run:
  `.\.venv\Scripts\python.exe scripts/test/quality_gates.py coverage --coverage-xml coverage.xml --config config/quality_gates.json`
- `GET /observability` is an in-memory runtime snapshot. It is intentionally
  lightweight and resets on process restart.
- Engine breakdown uses the explicit request override when present and falls
  back to `configured_default` when the request relies on the guild/default
  bot configuration.
- `GET /health` remains the canonical readiness check for deploy automation.
- Grafana dashboards are provisioned from
  `deploy/observability/grafana/dashboards/`.
- Prometheus alert rules are provisioned from
  `deploy/observability/prometheus-rules.yml` and are visible on the
  Prometheus `/alerts` page.
