# Project overview

This repository contains two independent applications:

- Discord bot
- Windows hotkey desktop app

Both must keep working independently after changes.

# Source of truth

Use `.specify/` as the canonical source of project guidance:

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/spec-template.md`
- `.specify/templates/tasks-template.md`

Tool-specific instructions should summarize and point to those docs instead of redefining policy.

# Core operating rules

1. Preserve clean architecture boundaries
2. Avoid duplication between `src/desktop/` and shared modules in `src/`
3. Prefer extracting shared interfaces, use cases, or services over copy-paste
4. Keep business logic out of presentation and infrastructure layers
5. Prefer small, incremental refactors
6. Validate both application modes before finishing relevant changes
7. Favor explicit contracts and typed results over implicit mapping-style payloads
8. Improve the repo's readability for the next contributor, not only the immediate change
9. Treat compatibility code as temporary by default and note when it should be removed

# Tech lead posture

- Optimize for consistency, predictability, and ease of future change
- Prefer the smallest change that improves architecture, clarity, or maintainability
- Avoid cosmetic refactors without a clear payoff in boundaries, contracts, onboarding, or validation
- When a module is large but acceptable as a composition root or runtime entrypoint, avoid splitting it without a concrete gain
- When a temporary facade, fallback, or compatibility path is introduced, keep it narrow and document the intended steady state

# Review emphasis

When evaluating code quality, prioritize:

1. boundary integrity
2. explicit contracts between modules
3. clarity of ownership and responsibility per module
4. onboarding readability for a new contributor
5. whether the change leaves the repo easier to evolve than before

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
- Use `specs/` for feature execution artifacts and planning outputs
- Do not keep implementation-history writeups in `docs/`
- Update `docs/README.md` when documentation structure or navigation changes
