# GitHub Copilot Instructions

This repository is a two-runtime Python platform:

- Discord bot
- Windows hotkey desktop app

The canonical source of project guidance lives in `.specify/`.

## Read first

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/spec-template.md`
- `.specify/templates/tasks-template.md`
- `docs/ARCHITECTURE.md`

## Non-negotiable rules

- Preserve independent execution of the bot and desktop app
- Do not duplicate logic between `src/desktop/` and shared modules in `src/`
- Keep business logic in `src/core/` or `src/application/`
- Let dependencies point inward according to clean architecture
- Prefer small, safe refactors over large rewrites

## Repository map

- `src/core/`: domain entities and pure rules
- `src/application/`: use cases and orchestration
- `src/infrastructure/`: adapters and external integrations
- `src/presentation/`: commands and controllers
- `src/desktop/`: desktop runtime, GUI, and Windows-specific adapters
- `src/bot.py`: Discord bot entrypoint
- `app.py`: desktop app entrypoint

## Validation expectations

Before closing a relevant change:

- run relevant tests
- check imports and architecture boundaries
- confirm bot startup still works
- confirm desktop app startup still works
- update docs when behavior or guidance changed

## Documentation placement

- Keep durable guides in `docs/`
- Put feature docs and implementation notes in `docs/features/`
- Keep `docs/README.md` in sync with navigation changes
