# GitHub Copilot Instructions

This repository is a two-runtime Python platform:

- Discord bot (`src/bot.py`)
- Windows hotkey desktop app (`app.py`)

Both must keep working independently after any change.

## Read first

- `docs/PROJECT_RULES.md` — binding repository rules
- `docs/architecture/ARCHITECTURE.md`

## Repository map

- `src/core/`: domain entities and pure rules
- `src/application/`: use cases and orchestration
- `src/infrastructure/`: adapters and external integrations
- `src/presentation/`: commands and controllers
- `src/desktop/`: desktop runtime, GUI, and Windows-specific adapters

## Non-negotiable rules

- `src/application/` and `src/presentation/` must not import
  `src.infrastructure` directly — define a contract inward and bind the adapter
  in a composition root
- Keep business logic in `src/core/` or `src/application/`
- Do not duplicate logic between `src/desktop/` and shared modules in `src/`
- Favor explicit contracts and typed results over implicit reusable payloads
- Write code, comments, docs, specs, tests, commit messages, and PR
  descriptions in English by default; another language only when localization
  or a locale fixture requires it

## Validation

Run the tests covering the changed path. When shared behavior or startup wiring
changes, confirm both bot and desktop startup. Call out validation gaps
explicitly.

## Documentation placement

- `docs/` for durable guides; update `docs/README.md` when navigation changes
- `openspec/` for change proposals, specs, and task lists
- No implementation-history writeups in `docs/`
