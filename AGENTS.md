# Project Overview

This repository contains two independent applications that must keep working
independently after changes:

- Discord bot (`src/bot.py`)
- Windows hotkey desktop app (`app.py`)

# Guidance

- `docs/PROJECT_RULES.md` — binding repository rules: architecture boundaries,
  where to start a change, contracts, validation, language and environment.
- `docs/architecture/ARCHITECTURE.md` — how the system is structured.
- `docs/README.md` — documentation index.

Change workflow runs through OpenSpec (`openspec/`). General engineering
practice comes from the agent definitions, not from files in this repo.

# Hard boundary

`src/application/` and `src/presentation/` must not import
`src/infrastructure/` directly. If shared logic needs infrastructure behavior,
define a contract inward and bind the concrete adapter in a composition root or
runtime layer.

# Validation

Validate both runtimes before finishing a change that touches shared behavior,
startup wiring, runtime flows or external adapters. Run the tests covering the
changed path. Call out any validation gap explicitly.

# Local agent assets

`.codex/` contains Codex skills and project-specific review playbooks.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community
structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or
instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
