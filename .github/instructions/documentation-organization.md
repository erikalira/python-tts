# Documentation Organization

Use `.specify/README.md` and `.specify/memory/constitution.md` as the canonical policy for documentation placement.

## Rules

- Keep the root `README.md` as the public entrypoint
- Keep top-level `docs/` focused on architecture, operating guides, and durable reference material
- Put feature planning and execution artifacts in `specs/`
- Do not keep implementation-history notes in `docs/`
- Update `docs/README.md` whenever documentation structure or navigation changes
- Update root links if a documentation move affects `README.md`

## Quick examples

- Architecture decision or operational guide -> `docs/`
- Feature specification, plan, or tasks -> `specs/`
- Workflow rule or instruction governance -> `.specify/`
