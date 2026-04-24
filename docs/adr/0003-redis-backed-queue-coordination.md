# ADR 0003: Use Redis For Queue Coordination

## Status

Accepted

## Context

The bot processes guild-scoped TTS queues. A single in-memory queue is enough
for local development, but distributed workers need shared queue state, locks,
and processing leases.

## Decision

Use Redis as the production queue backend and coordination mechanism. Keep the
in-memory queue for local and test paths.

## Consequences

- Multiple workers can coordinate through Redis-backed locks and leases.
- Redis queue state is operational state, while Postgres remains the durable
  source for bot configuration.
- Redis incidents should usually recover by restarting, clearing scoped queue
  state, or recreating transient data rather than treating Redis as the primary
  business database.

