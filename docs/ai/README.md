# AI Governance

This directory is the canonical source of truth for AI-facing project guidance.

Use these files as the shared foundation for:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/instructions/*`
- `.codex/skills/*`

## Canonical files

- `project-context.md`: product shape, entrypoints, and repo map
- `architecture-rules.md`: clean architecture boundaries and dependency rules
- `engineering-standards.md`: coding, testing, review, and change expectations
- `documentation-policy.md`: where docs belong and how to maintain the index
- `change-playbooks.md`: step-by-step guidance for common change types

## Recommended companion docs

These are not canonical policy files, but they are useful when reasoning about concrete changes:

- `../RUNTIME_FLOWS.md`: entrypoints, composition roots, and main runtime paths
- `../ARCHITECTURE_TRANSITIONS.md`: temporary compatibility and steady-state guidance
- `../CHANGE_MAP.md`: where to start for each kind of change
- `../REVIEW_CHECKLIST.md`: short review checklist for contracts, boundaries, and runtime safety
- `../TRANSITION_CLEANUP.md`: operational rule for temporary compatibility cleanup
- `../CHANGE_EXAMPLES.md`: concrete examples of where a change should start and land

## Working rule

Keep stable policy here. Tool-specific files should summarize and point here instead of duplicating long policy blocks.
