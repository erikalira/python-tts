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

Change workflow runs through OpenSpec (`openspec/`).

# Precedence

General engineering practice comes from the installed agent definitions, not
from files in this repo. This repo owns project-specific rules: where the two
overlap, `docs/PROJECT_RULES.md` wins for anything specific to this codebase —
layers, runtimes, file paths, validation.

# Hard boundary

`src/application/` and `src/presentation/` must not import
`src/infrastructure/` directly. If shared logic needs infrastructure behavior,
define a contract inward and bind the concrete adapter in a composition root or
runtime layer.

This is enforced by `tests/unit/test_architecture_boundaries.py`, which also
guards the full inward dependency flow and keeps the desktop runtime
independent of the bot runtime. Run it before finishing a change that moves
imports between layers.

# Production deployment

The Discord bot runs in production on a **GCP e2-micro** (`us-central1`, amd64),
not on the OCI Ampere A1 host the deployment guide presents as preferred. The
OCI environment is fully provisioned except for the instance: every apply so far
has returned `Out of host capacity`. Its network resources cost nothing and are
left in place, so a later `tofu apply` creates only the missing instance.

**Deploys are manual, by decision.** The `Deploy Cloud VM` workflow connects over
SSH from a GitHub-hosted runner, and the firewall restricts port 22 to the
maintainer's own address. Do not propose its real-deploy mode or widening
`ssh_allowed_cidrs` to GitHub's runner ranges. Deploy over SSH instead:

```bash
ssh ubuntu@<HOST> '/opt/python-tts/scripts/vm-deploy.sh v1.2.5'
ssh ubuntu@<HOST> '/opt/python-tts/scripts/vm-deploy.sh --rollback'
```

The workflow's `dry_run: true` mode does work from CI and is worth running first:
it confirms a release tag exists for the target architecture.

Two things that break quietly:

- The GCP public IP is ephemeral, so recreating the instance changes it.
- SSH is allowlisted to one address; if the maintainer's IP changes, SSH stops
  working until `ssh_allowed_cidrs` is updated and `tofu apply` re-run.

Release tags publish to GHCR **without the leading `v`**: `v1.2.3` becomes
`1.2.3`. The deploy tooling accepts the git-tag form and resolves it. Create the
tag only after committing — the Release workflow builds whatever commit the tag
points at.

See `docs/deploy/SMALL_CLOUD_VM_DEPLOY.md` and
`docs/adr/0008-oci-ampere-a1-deployment-target.md`.

# Validation

Validate both runtimes before finishing a change that touches shared behavior,
startup wiring, runtime flows or external adapters. Run the tests covering the
changed path. Call out any validation gap explicitly.

# Local agent assets

`.codex/` contains Codex skills and project-specific review playbooks. They are
tool-specific execution detail; where one restates repository policy,
`docs/PROJECT_RULES.md` is authoritative.

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
