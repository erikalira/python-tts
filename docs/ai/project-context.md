# Project Context

## Product shape

This repository contains two independent applications:

- Discord bot
- Windows hotkey desktop app

Both must keep working independently after changes.

## Primary goals

- Reuse shared logic across both applications
- Avoid duplication between `src/desktop/` and the shared layers in `src/`
- Keep business rules inside clean architecture boundaries
- Support incremental refactors over large rewrites

## Important entrypoints

- `src/bot.py`: Discord bot and HTTP runtime
- `app.py`: Windows desktop app entrypoint
- `src/desktop/app/bootstrap.py`: desktop composition root
- `src/desktop/app/desktop_app.py`: desktop runtime

## Shared layer map

- `src/core/`: entities, value objects, pure domain rules
- `src/application/`: use cases, orchestration, shared application services
- `src/infrastructure/`: adapters, IO, persistence, integrations, external providers
- `src/presentation/`: controllers, commands, entrypoint-facing flow
- `src/desktop/`: desktop-specific runtime, adapters, and GUI behavior

## Repository expectations

- Prefer small, safe changes
- Preserve import clarity and boundary direction
- Keep the repo understandable for both humans and AI tooling
- Update documentation when behavior, architecture, or operational flow changes

## Quality bar

The target quality bar is not only "clean code", but "tech lead friendly" code:

- explicit module contracts instead of loosely shaped payloads when practical
- clear ownership of responsibilities per file or module
- predictable composition paths for both runtimes
- onboarding readability for contributors who did not author the feature
- refactors that improve evolvability instead of only rearranging code

## Legacy posture

Legacy in this repository should be treated as one of three categories:

- intentional compatibility that still protects users or entrypoints
- temporary transition code introduced during incremental refactors
- avoidable leftover complexity that should be reduced when touching the area

When a compatibility layer or facade is kept temporarily, prefer documenting the intended steady state rather than silently normalizing it as permanent structure.
