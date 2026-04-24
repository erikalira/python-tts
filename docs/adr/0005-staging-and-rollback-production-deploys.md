# ADR 0005: Require Staging And Rollback For Production Deploys

## Status

Accepted

## Context

The Docker production stack includes Redis, Postgres, the bot, health checks,
and observability services. Releasing directly to production without a rehearse
or rollback point increases incident risk.

## Decision

Production releases should pass through a staging environment that mirrors the
production compose shape closely enough to validate startup, readiness, Redis,
Postgres, and the bot smoke flow. Every production release must identify a
rollback point before deploy.

## Consequences

- Release checklists must include staging validation and rollback metadata.
- Rollback drills should stay current with the actual deploy shape.
- Staging does not need production scale, but it must exercise the same
  integration contracts and dependency readiness checks.

