# ADR 0002: Use Postgres For Production Bot Configuration

## Status

Accepted

## Context

The bot needs durable guild and user TTS settings. JSON storage is simple for
local development, but production needs a backend that survives container
replacement and supports future operational growth.

## Decision

Use Postgres as the production configuration storage backend. Keep JSON storage
available for local and simple deployments.

## Consequences

- Production config survives bot container restarts and rebuilds.
- Backup and restore procedures focus on Postgres logical dumps.
- Runtime code must keep storage behind inward-facing contracts so application
  logic does not depend on Postgres directly.

