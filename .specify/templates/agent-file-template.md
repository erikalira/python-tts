# [PROJECT NAME] Development Guidelines

Auto-generated from Spec Kit planning artifacts. Last updated: [DATE]

## Canonical Guidance

Treat `docs/ai/` as the source of truth for project guidance:

- `docs/ai/project-context.md`
- `docs/ai/architecture-rules.md`
- `docs/ai/engineering-standards.md`
- `docs/ai/documentation-policy.md`
- `docs/ai/change-playbooks.md`

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
- Documentation updates belong in `docs/` or `docs/features/`, with navigation reflected in `docs/README.md`.

## Recent Changes

[LAST 3 FEATURES AND WHAT THEY ADDED]

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
