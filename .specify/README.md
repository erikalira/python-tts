# Spec Kit Canonical Guidance

This directory is the canonical source of truth for repository workflow and
project guidance.

Use these files as the shared foundation for:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.codex/skills/*`
- feature specs and implementation plans in `specs/`

## Canonical files

- `memory/constitution.md`: repository rules, architecture constraints, review
  gates, and governance
- `templates/spec-template.md`: mandatory structure for feature specifications
- `templates/plan-template.md`: mandatory structure for implementation plans
- `templates/tasks-template.md`: mandatory structure for execution task lists
- `templates/agent-file-template.md`: baseline guidance format for agent-facing
  instruction files
- `review-checklist.md`: review and self-review checklist for code changes
- `transition-cleanup.md`: temporary compatibility and cleanup rule
- `change-map.md`: where to start for each kind of change
- `change-examples.md`: concrete examples of starting points and target layers

## Companion docs

These are not the canonical rules source, but they remain useful when changing
code or operations:

- `docs/ARCHITECTURE.md`
- `docs/RUNTIME_FLOWS.md`
- `docs/ARCHITECTURE_TRANSITIONS.md`
- `docs/DEPENDENCY_MAINTENANCE.md`
- `docs/TESTING.md`

## Working rule

Keep stable project rules and workflow standards in `.specify/`. Durable
product and operational guides stay in `docs/`, and feature-specific execution
artifacts stay in `specs/`.
