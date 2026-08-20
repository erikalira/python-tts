# Documentation Organization

Binding rules live in `docs/PROJECT_RULES.md`.

## Rules

- Keep the root `README.md` as the public entrypoint
- Keep top-level `docs/` focused on architecture, operating guides, and durable reference material
- Put change proposals, specs, and task lists in `openspec/`
- Do not keep implementation-history notes in `docs/`
- Update `docs/README.md` whenever documentation structure or navigation changes
- Update root links if a documentation move affects `README.md`
- Write documentation, specs, instruction files, and AI-generated project
  artifacts in English by default

## Quick examples

- Architecture decision or operational guide -> `docs/`
- Change proposal, spec, or tasks -> `openspec/`
- Tool-specific agent skill or local playbook -> `.codex/`
