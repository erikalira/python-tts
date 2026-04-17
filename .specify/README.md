# Spec Kit Canonical Guidance

This directory is the canonical source of truth for repository workflow,
governance, and AI-facing guidance.

Use `.specify/` as the shared foundation for:

- `AGENTS.md`
- `.github/copilot-instructions.md`
- `.github/copilot-workspace.yml`
- project-specific guidance embedded in `.agents/` and `.codex/`
- feature specs and implementation plans in `specs/`

Those files may summarize repository policy, but they must not evolve into a
second authority.

## Canonical files

- `memory/constitution.md`: non-negotiable rules, review gates, and governance
- `templates/spec-template.md`: required shape for feature specifications
- `templates/plan-template.md`: required shape for implementation plans
- `templates/tasks-template.md`: required shape for execution task lists
- `templates/agent-file-template.md`: pattern for derivative agent guidance
- `review-checklist.md`: review and self-review rubric for code changes
- `transition-cleanup.md`: temporary compatibility and cleanup rule
- `change-map.md`: where to start for each kind of change
- `change-examples.md`: concrete examples of starting points and target layers

## AI Guidance Hierarchy

When instructions appear in multiple places, use this order of precedence:

1. `.specify/memory/constitution.md`
2. `.specify/templates/*.md`
3. `.specify/review-checklist.md`, `transition-cleanup.md`, `change-map.md`,
   and `change-examples.md`
4. Derivative files such as `AGENTS.md`, `.github/copilot-instructions.md`,
   and `.github/copilot-workspace.yml`

If a derivative file drifts from `.specify/`, `.specify/` wins and the
derivative file should be corrected.

## Staff-Level Working Standard

Contributors and AI agents should optimize for repository-level change quality,
not local cleverness.

- Prefer the smallest change that improves boundaries, contracts, readability,
  or runtime safety.
- Do not introduce abstractions unless they remove duplication, clarify
  ownership, or make future change safer.
- Document the intended steady state whenever a temporary facade, compatibility
  path, or migration layer is introduced.
- Delete obsolete paths when the replacement is proven safe instead of
  normalizing permanent dual paths.
- Treat onboarding clarity as an engineering requirement, not a nice-to-have.

## Companion docs

These are not the canonical rules source, but they remain useful when changing
code or operations:

- `docs/getting-started/SETUP.md`
- `docs/getting-started/TESTING.md`
- `docs/architecture/ARCHITECTURE.md`
- `docs/architecture/RUNTIME_FLOWS.md`
- `docs/architecture/ARCHITECTURE_TRANSITIONS.md`
- `docs/maintenance/DEPENDENCY_MAINTENANCE.md`

## Environment baseline

Use the repository virtual environment as the default Python runtime for local
development, validation, and agent-run commands. Do not rely on a globally
installed Python when the repo `.venv` is available.

- Windows PowerShell: `.\.venv\Scripts\python.exe`
- Ubuntu / WSL / macOS: `.venv/bin/python`

When installing dependencies or running tests, prefer commands such as
`.\.venv\Scripts\python.exe -m pip install -r requirements-test.txt` and
`.\.venv\Scripts\python.exe -m pytest`.

## Text and encoding baseline

Use UTF-8 source files by default when editing repository text and code.
Prefer natural Portuguese in user-facing strings instead of escaped Unicode
sequences.

- Write Portuguese accents directly when the file format supports UTF-8.
- Do not replace Portuguese characters with Unicode escapes unless the target
  format explicitly requires escapes.
- Prefer readable Portuguese text in bot messages, desktop labels, docs, and
  tests that assert user-facing content.
- Keep ASCII-only text only when required by external tools, legacy formats, or
  existing file constraints that would break with UTF-8 characters.

## Working rule

Keep stable project rules and workflow standards in `.specify/`. Durable
product and operational guides stay in `docs/`, and feature-specific execution
artifacts stay in `specs/`.
