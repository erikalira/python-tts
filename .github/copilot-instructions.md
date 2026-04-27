<!-- Based on .specify/memory/constitution.md v1.3.0 -->
<!-- Last synced: 2026-04-27 -->

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
- `.specify/review-checklist.md`
- `.specify/memory/ai-pitfalls.md`
- `docs/architecture/ARCHITECTURE.md`

This file is a derivative summary. If it disagrees with `.specify/`, follow
`.specify/`.

## Senior/Staff Decision Standard

- Optimize for repository-level maintainability, not a local shortcut
- Prefer the smallest architecture-safe step that improves boundaries,
  contracts, readability, or runtime safety
- Introduce abstractions only when they solve a concrete repository problem
- Keep compatibility code narrow, visible, and documented with the intended
  steady state
- Delete obsolete paths when safe instead of normalizing permanent dual flows

## Non-negotiable rules

- Preserve independent execution of the bot and desktop app
- Do not duplicate logic between `src/desktop/` and shared modules in `src/`
- Keep business logic in `src/core/` or `src/application/`
- Let dependencies point inward according to clean architecture
- Prefer small, safe refactors over large rewrites
- Favor explicit contracts and typed results over implicit reusable payloads
- Write code, comments, docs, specs, tests, commit messages, PR descriptions,
  and AI-generated project artifacts in English by default
- Use another language in user-facing runtime text only when localization,
  language-specific behavior, or a locale fixture explicitly requires it

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
- call out validation gaps explicitly if a runtime check could not be performed

## Documentation placement

- Keep durable guides in `docs/`
- Put feature planning and execution artifacts in `specs/`
- Do not keep implementation-history writeups in `docs/`
- Keep `docs/README.md` in sync with navigation changes
- Keep stable AI governance in `.specify/`, not in ad-hoc tool-specific files

## Local agent assets

- `.agents/` contains Spec Kit skills and agent workflow helpers
- `.codex/` contains Codex skills and architecture/review playbooks
- Treat both as derivative of `.specify/` for repository policy
