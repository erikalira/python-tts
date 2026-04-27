# Load Testing

This guide documents the lightweight queue load baseline used before adding
heavier external load tools.

## Current Baseline

The first load slice lives in `tests/load/test_queue_load_baseline.py` and
targets the in-memory queue behavior that the bot uses in local development and
simple deploys.

It checks:

- enqueue throughput for a bounded batch
- queue size after accepted items
- backpressure when the configured queue capacity is reached

The CI job is intentionally non-blocking while the repository gathers baseline
history. Promote it to a blocking release gate only after the expected
throughput and latency thresholds are known for the target runner class.

## Local Run

```powershell
$env:QUEUE_LOAD_REPORT_PATH=".test-artifacts/load/queue-load-baseline.json"
uv run pytest tests/load --tb=short -v --no-cov
```

The report is written only when `QUEUE_LOAD_REPORT_PATH` is set.
