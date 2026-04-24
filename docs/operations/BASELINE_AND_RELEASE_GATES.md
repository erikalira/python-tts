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

## Release Gates

### Discord bot

- Required automated gate:
  `.\.venv\Scripts\python.exe -m pytest tests/unit tests/integration tests/smoke/test_release_gates.py -k "bot or release_gates"`
- Minimum expectation:
  unit coverage stays green, critical integration paths stay green, and the
  bot health/observability endpoints remain available.

### Desktop app

- Required automated gate:
  `.\.venv\Scripts\python.exe -m pytest tests/unit/desktop tests/smoke/test_release_gates.py -k "desktop or release_gates"`
- Minimum expectation:
  startup still succeeds, hotkey/tray services can start, and the minimal bot
  interaction flow still works.

## Notes

- `GET /observability` is an in-memory runtime snapshot. It is intentionally
  lightweight and resets on process restart.
- Engine breakdown uses the explicit request override when present and falls
  back to `configured_default` when the request relies on the guild/default
  bot configuration.
- `GET /health` remains the canonical readiness check for deploy automation.
