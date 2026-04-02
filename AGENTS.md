# Project overview

This repository contains two separate applications:

- Discord bot
- Windows hotkey app

# Architecture rules

- Target architecture is clean architecture
- Avoid duplication between `standalone` and `src`
- Prefer extracting interfaces/adapters instead of copying logic
- Reuse use cases and services whenever possible
- Preserve independent execution of both applications

# Important paths

- `bot.py`
- `app.py`
- `standalone/`
- `src/application/`
- `src/core/`
- `src/infrastructure/`
- `src/presentation/`

# Change policy

When making changes:

1. Keep both applications working independently
2. Prefer small, incremental refactors
3. Check impact on bot flow and Windows hotkey flow
4. Avoid introducing logic into outer layers that belongs in core/application

# Documentation policy

- Keep `docs/` focused on main structure docs and operational guides
- Add documentation for new features, feature iterations, and implementation notes under `docs/features/`
- When adding or updating feature docs, update `docs/README.md` so the index reflects the new location
- Prefer feature-specific filenames in `docs/features/` instead of expanding the top-level `docs/` directory

# Validation

Before finishing:

- run relevant tests
- verify imports did not break architecture boundaries
- confirm bot startup still works
- confirm Windows app startup still works

# Strict rules

- Never duplicate logic between `standalone` and `src`
- Never place business logic in presentation or infrastructure
- Always prefer reuse over copy-paste
- If duplication is found, refactor instead of extending it
