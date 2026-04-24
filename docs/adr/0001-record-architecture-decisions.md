# ADR 0001: Record Architecture Decisions

## Status

Accepted

## Context

The repository supports a Discord bot and a Windows desktop app. Several
decisions affect both runtimes or production operations, and those decisions
need durable rationale beyond implementation comments.

## Decision

Use ADRs in `docs/adr/` for major architecture, persistence, observability, and
deployment decisions. Keep governance rules in `.specify/`; ADRs record why a
specific technical choice was made.

## Consequences

- Major decisions have a stable place for context and tradeoffs.
- Reviews can ask for an ADR when a change introduces long-lived operational or
  architecture impact.
- ADRs must stay concise and should be updated or superseded when the steady
  state changes.

