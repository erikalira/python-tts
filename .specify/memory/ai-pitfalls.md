# Common Pitfalls For AI Contributors

**Constitution compatibility**: v1.2.1
**Last updated**: 2026-04-26
**Canonical source**: `.specify/memory/constitution.md`
**Derived consumers**: `AGENTS.md`, `.github/copilot-instructions.md`,
`.github/copilot-workspace.yml`, `.codex/skills/*`, `.agents/skills/*`

Use this file as a quick reminder before planning, implementing, or reviewing
AI-assisted changes in this repository. The constitution remains authoritative.

## Boundary Pitfalls

- Importing `src.infrastructure` from `src.application` or `src.presentation`.
- Moving business policy into GUI handlers, Discord command handlers, HTTP
  controllers, or adapter code.
- Treating `src/desktop/` as a second shared application layer instead of a
  Windows-specific runtime.
- Adding infrastructure behavior to shared logic instead of defining an inward
  contract and binding the adapter in a composition root.

## Contract Pitfalls

- Passing reusable behavior through loosely shaped dictionaries when a typed
  result, DTO, protocol, or named contract would make the boundary clear.
- Returning mixed success/error payloads that force callers to inspect incidental
  keys.
- Making temporary compatibility facades look like permanent public APIs.
- Updating only one runtime path when a shared contract is consumed by both the
  bot and desktop app.

## Duplication Pitfalls

- Copying desktop behavior into shared modules without separating Windows-only
  concerns.
- Copying bot flow logic into desktop runtime code instead of extracting a
  shared use case.
- Keeping old and new flows permanently active after a migration succeeds.
- Creating a new abstraction because it is familiar rather than because it
  removes concrete duplication, ambiguity, or change risk.

## Documentation Pitfalls

- Updating `AGENTS.md`, Copilot files, or local skills without updating
  `.specify/` first when the rule is durable.
- Adding durable architecture or workflow guidance under `docs/` instead of
  `.specify/`.
- Forgetting `docs/README.md` after adding, moving, or retiring durable docs.
- Letting derivative instruction files omit the constitution version they
  summarize.

## Validation Pitfalls

- Running tests for only the runtime you touched when shared behavior changed.
- Claiming desktop validation without checking startup, hotkey wiring, or GUI
  behavior when those paths changed.
- Claiming bot validation without checking startup, command wiring, HTTP
  routes, or voice delivery when those paths changed.
- Hiding validation gaps instead of naming what could not be checked.
