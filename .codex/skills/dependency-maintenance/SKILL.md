---
name: dependency-maintenance
description: Check package versions, update Python dependencies, and validate dependency migrations with repository-specific good practices. Use when Codacy reports vulnerable packages, when requirements files need updates, or when Codex should run the project's dependency upgrade workflow with tests and smoke checks.
---

# Canonical references

Read these first:

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/review-checklist.md`
- `docs/DEPENDENCY_MAINTENANCE.md`
- `docs/TESTING.md`

For the step-by-step command checklist, read:

- `references/workflow.md`

# Workflow

1. Identify whether the change belongs in `requirements.txt`, `requirements-test.txt`, or both
2. Inspect current constraints and installed versions with `scripts/utils/dependency_maintenance.py report`
3. Prefer the smallest package set that resolves the issue
4. Upgrade in `.venv` first, then write the validated version back into the requirement file
5. Run `scripts/utils/dependency_maintenance.py validate`
6. Run integration tests or manual checks when the dependency touches real providers, Discord runtime, or desktop runtime
7. Update docs if the maintenance flow or dependency policy changes

# Output

- package upgrade plan
- exact commands used
- requirement files changed
- validation run and any remaining gaps
