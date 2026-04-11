# [PROJECT NAME] Development Guidelines

Auto-generated from Spec Kit planning artifacts. Last updated: [DATE]

## Canonical Guidance

Treat `.specify/` as the source of truth for project guidance:

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/templates/spec-template.md`
- `.specify/templates/plan-template.md`
- `.specify/templates/tasks-template.md`

Use these docs instead of restating long policy sections in agent-specific files.

## Core Rules

- Preserve independent execution of the Discord bot and Windows desktop app.
- Keep business logic in `src/core/` or `src/application/`.
- Avoid duplication between `src/desktop/` and shared modules in `src/`.
- Prefer small, explicit, reversible changes over broad rewrites.
- Keep temporary compatibility code narrow and document the intended steady state.

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

## Recent Changes

[LAST 3 FEATURES AND WHAT THEY ADDED]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
