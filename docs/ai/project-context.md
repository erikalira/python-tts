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
