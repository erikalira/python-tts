<!-- Based on .specify/memory/constitution.md v1.3.0 -->
<!-- Last synced: 2026-04-27 -->

# Documentation Organization

Use `.specify/README.md` and `.specify/memory/constitution.md` as the canonical
policy for documentation placement.

## Rules

- Keep the root `README.md` as the public entrypoint
- Keep top-level `docs/` focused on architecture, operating guides, and durable reference material
- Put feature planning and execution artifacts in `specs/`
- Do not keep implementation-history notes in `docs/`
- Update `docs/README.md` whenever documentation structure or navigation changes
- Update root links if a documentation move affects `README.md`
- Keep stable AI governance in `.specify/`, not in `docs/ai/`, `docs/features/`,
  or other ad-hoc locations
- Keep `.agents/`, `.codex/`, and GitHub instruction files derivative of
  `.specify/` when they describe repository policy
- Write documentation, specs, instruction files, and AI-generated project
  artifacts in English by default

## Quick examples

- Architecture decision or operational guide -> `docs/`
- Feature specification, plan, or tasks -> `specs/`
- Workflow rule or instruction governance -> `.specify/`
- Tool-specific agent skill or local playbook -> `.agents/` or `.codex/`, with
  `.specify/` as the policy source
