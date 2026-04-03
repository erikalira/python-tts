# Project overview

This repository contains two independent applications:

- Discord bot
- Windows hotkey desktop app

Both must keep working independently after changes.

# Source of truth

Use `docs/ai/` as the canonical source of project guidance:

- `docs/ai/project-context.md`
- `docs/ai/architecture-rules.md`
- `docs/ai/engineering-standards.md`
- `docs/ai/documentation-policy.md`
- `docs/ai/change-playbooks.md`

Tool-specific instructions should summarize and point to those docs instead of redefining policy.

# Core operating rules

1. Preserve clean architecture boundaries
2. Avoid duplication between `src/desktop/` and shared modules in `src/`
3. Prefer extracting shared interfaces, use cases, or services over copy-paste
4. Keep business logic out of presentation and infrastructure layers
5. Prefer small, incremental refactors
6. Validate both application modes before finishing relevant changes

# Important paths

- `src/bot.py`
- `app.py`
- `src/core/`
- `src/application/`
- `src/infrastructure/`
- `src/presentation/`
- `src/desktop/`

# Documentation rule

- Use top-level `docs/` for durable guides and architecture material
- Use `docs/features/` for feature docs, feature iterations, and implementation notes
- Update `docs/README.md` when documentation structure or navigation changes
