# [PROJECT NAME] Development Guidelines

Auto-generated from Spec Kit planning artifacts. Last updated: [DATE]

## Canonical Guidance

Treat `.specify/` as the source of truth for project guidance:

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/templates/spec-template.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/tasks-template.md`

This file is a derivative summary. Keep it short, repo-specific, and aligned to
the canonical docs above instead of restating long policy sections.

## Operating Standard

- Optimize for repository-level maintainability, not local cleverness.
- Prefer the smallest change that improves boundaries, contracts, readability,
  or runtime safety.
- Introduce abstractions only when they remove duplication, clarify ownership,
  or make future changes safer.
- Keep temporary compatibility paths narrow and document the intended steady
  state.
- Delete obsolete paths when safe instead of normalizing permanent dual flows.

## Core Rules

- Preserve independent execution of the Discord bot and Windows desktop app.
- Keep business logic in `src/core/` or `src/application/`.
- Avoid duplication between `src/desktop/` and shared modules in `src/`.
- Prefer small, explicit, reversible changes over broad rewrites.
- Favor explicit contracts and typed results over implicit mapping-style payloads.

## Active Technologies

[EXTRACTED FROM ALL PLAN.MD FILES]

## Repository Map

```text
[ACTUAL STRUCTURE FROM PLANS]
```

## Commands

[ONLY COMMANDS FOR ACTIVE TECHNOLOGIES]

## Code Style

[LANGUAGE-SPECIFIC, ONLY FOR LANGUAGES IN USE]

## Spec Kit Workflow

- Feature specs live in `specs/<feature>/`.
- Planning and governance templates live in `.specify/`.
- Implementation plans and tasks must follow the constitution in `.specify/memory/constitution.md`.
- Documentation updates belong in `docs/`, with navigation reflected in `docs/README.md`.
- Derivative AI instruction files should summarize `.specify/`, not compete with it.

## Recent Changes

[LAST 3 FEATURES AND WHAT THEY ADDED]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
