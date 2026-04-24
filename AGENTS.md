# Project Overview

This repository contains two independent applications:

- Discord bot
- Windows hotkey desktop app

Both must keep working independently after changes.

# Canonical Guidance

Use `.specify/` as the source of truth for repository workflow and AI guidance:

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/templates/spec-template.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/tasks-template.md`
- `.specify/review-checklist.md`

This file is a derivative summary. If guidance conflicts, `.specify/` wins.

# Senior/Staff Operating Standard

1. Optimize for repository-level maintainability, not local cleverness
2. Preserve clean architecture boundaries and inward dependency flow
3. Avoid duplication between `src/desktop/` and shared modules in `src/`
4. Prefer extracting shared interfaces, use cases, or services over copy-paste
5. Keep business logic out of presentation, infrastructure, and GUI layers
6. Favor explicit contracts and typed results over implicit mapping-style payloads
7. Prefer the smallest reversible refactor that meaningfully improves the codebase
8. Treat compatibility code as temporary, narrow, and documented with the intended steady state
9. Remove obsolete paths when safe instead of normalizing permanent dual flows
10. Improve onboarding readability for the next contributor, not only the immediate change

# Tech Lead Posture

- Choose the smallest architecture-safe change with clear ownership
- Introduce abstractions only when they remove duplication, shrink ambiguity, or lower future change cost
- Avoid cosmetic refactors without a concrete payoff in boundaries, contracts, validation, or readability
- When a file is acting as a composition root or runtime coordinator, do not split it unless that split reduces real complexity
- Make non-goals, tradeoffs, and cleanup expectations explicit when the change could drift or leave residue behind

# Validation

- Validate both application modes before finishing relevant changes
- Run the tests that cover the changed path directly
- Call out any validation gap explicitly if full runtime validation is not possible

# Important Paths

- `src/bot.py`
- `app.py`
- `src/core/`
- `src/application/`
- `src/infrastructure/`
- `src/presentation/`
- `src/desktop/`

# Documentation Rule

- Use top-level `docs/` for durable guides and architecture material
- Use `specs/` for feature execution artifacts and planning outputs
- Keep stable AI governance in `.specify/`, not scattered across tool-specific files
- Do not keep implementation-history writeups in `docs/`
- Update `docs/README.md` when documentation structure or navigation changes
