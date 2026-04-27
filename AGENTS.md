<!-- Based on .specify/memory/constitution.md v1.3.0 -->
<!-- Last synced: 2026-04-27 -->

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
- `.specify/memory/ai-pitfalls.md`

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

Hard boundary:
- `src/application/` and `src/presentation/` must not import `src/infrastructure/` directly.
- If shared logic needs infrastructure behavior, define a contract inward and bind the concrete adapter in a composition root or runtime layer.

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

# Language Rule

- Write repository code, comments, documentation, specs, tests, commit messages,
  pull request descriptions, and AI-generated project artifacts in English
- Use another language in user-facing runtime text only when localization,
  language-specific behavior, or a locale fixture explicitly requires it

# Local Agent Assets

- `.agents/` contains Spec Kit agent skills and workflow helpers
- `.codex/` contains Codex skills and project-specific review playbooks
- Both are derivative of `.specify/` for repository policy and must stay synchronized when canonical guidance changes
