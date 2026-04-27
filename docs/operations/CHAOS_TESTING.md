# Chaos Testing

This repository starts chaos coverage with deterministic dependency-failure
tests before introducing runtime fault injection.

## Current Scope

`tests/chaos/test_dependency_failure_modes.py` covers:

- Postgres connect timeout or unavailable storage adapter
- Redis ping failure
- stopped queue worker

The tests exercise readiness behavior without requiring real Redis or Postgres
outages. They make sure `/ready` can report `not_ready` with a useful dependency
detail before traffic is routed to a broken bot runtime.

## Local Run

```powershell
uv run pytest tests/chaos --tb=short -v --no-cov
```

## Future Runtime Drills

After staging is available, add drills that stop the real Redis and Postgres
services under Docker Compose or Kubernetes and verify:

- `GET /ready` returns `503`
- logs identify the failed dependency without leaking credentials
- the bot returns to `ready` after the dependency recovers
- queued work does not duplicate after Redis recovery
