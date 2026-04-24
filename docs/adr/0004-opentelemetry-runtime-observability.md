# ADR 0004: Use OpenTelemetry With No-Op Fallback

## Status

Accepted

## Context

The bot needs traceability across HTTP entrypoints, queue processing, and TTS
engine execution. Local development should remain simple when an OTLP collector
is not available.

## Decision

Use manually wired OpenTelemetry tracing and metrics in runtime boundaries,
enabled through environment configuration. When disabled or unavailable, the
runtime falls back to no-op behavior.

## Consequences

- Production can export spans and metrics without coupling application logic to
  a specific observability backend.
- Local development and tests do not require a collector.
- Operators still need dashboards and alerts that consume the emitted signals.

