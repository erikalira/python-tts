# Mutation Testing

This repository uses `mutmut` as an optional mutation-testing baseline for
critical pure Python behavior.

## Scope

The first baseline is intentionally narrow:

- `src/core/`
- `src/application/tts_text.py`
- `src/application/rate_limiting.py`
- `src/application/desktop_tts.py`

These modules are fast to test and do not require Discord, Windows hooks,
Redis, Postgres, audio devices, or GUI services.

## Local Run

`mutmut` does not support native Windows execution. Run it from Linux, CI, or
WSL:

```bash
uv sync --locked --group test --group mutation
uv run pytest tests/unit/core tests/unit/application/test_desktop_tts.py tests/unit/application/test_use_cases.py --tb=short -v
uv run mutmut run
uv run mutmut results
```

The CI mutation job is non-blocking while the baseline is noisy. Treat survived
mutants as backlog for focused tests; raise the bar only after the first reports
are triaged.
