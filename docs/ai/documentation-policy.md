# Documentation Policy

## Documentation layout

- `README.md` in the repo root is the public entrypoint
- `docs/` stores architecture docs, operational guides, and shared reference material
- `docs/features/` stores feature docs, feature iterations, and implementation notes
- `docs/README.md` is the index for the documentation tree and must stay current
- `docs/ai/` stores canonical AI governance and instruction policy

## Placement rules

- New feature documentation goes under `docs/features/`
- Updates to architecture or operating guides stay in top-level `docs/`
- Tool-specific instruction files should point to canonical docs instead of restating long policy sections
- If a documentation move changes navigation, update links in `README.md` and `docs/README.md`

## When to update docs

Update documentation when a change affects:

- architecture boundaries
- startup or runtime behavior
- operator workflows
- desktop UX that users rely on
- contributor or AI guidance
- onboarding clarity for a changed flow
- the intended steady state after introducing temporary compatibility or facade code

## Naming guidance

- Prefer feature-specific filenames in `docs/features/`
- Keep top-level `docs/` focused on durable guides, not change logs
- Write docs to explain intent, constraints, and operating expectations

## Documentation quality bar

Good documentation in this repository should:

- explain why the structure exists, not only what files changed
- help a new contributor find the entrypoint and main flow quickly
- distinguish durable architecture from temporary transition structure
- avoid over-specifying implementation details that will drift quickly
