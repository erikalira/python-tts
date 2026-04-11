<!--
Sync Impact Report
- Version change: 0.0.0 -> 1.0.0
- Modified principles:
  - Placeholder Principle 1 -> I. Clean Architecture Boundaries
  - Placeholder Principle 2 -> II. Shared Logic Before Duplication
  - Placeholder Principle 3 -> III. Incremental Change With Explicit Contracts
  - Placeholder Principle 4 -> IV. Dual-Runtime Safety And Validation
  - Placeholder Principle 5 -> V. Documentation As Operational Memory
- Added sections:
  - Repository Constraints
  - Workflow And Review Gates
- Removed sections:
  - None
- Templates requiring updates:
  - updated: .specify/templates/plan-template.md
  - updated: .specify/templates/spec-template.md
  - updated: .specify/templates/tasks-template.md
  - updated: .specify/templates/agent-file-template.md
  - updated: docs/README.md
  - updated: README.md
- Follow-up TODOs:
  - None
-->
# TTS Hotkey Windows Constitution

## Core Principles

### I. Clean Architecture Boundaries
All changes MUST preserve inward dependency flow across `src/core/`,
`src/application/`, `src/infrastructure/`, `src/presentation/`, and
`src/desktop/`. Business rules MUST live in `src/core/` or `src/application/`
unless an explicit, documented exception is required. Presentation, runtime, and
infrastructure code MUST delegate instead of absorbing product policy.

Rationale: This repository already supports two runtimes. Boundary drift makes
the bot and desktop app harder to evolve independently.

### II. Shared Logic Before Duplication
Behavior reused by the Discord bot and Windows desktop app MUST be extracted into
shared interfaces, use cases, or services before copy-paste is introduced or
expanded. `src/desktop/` MUST reuse shared modules in `src/` whenever the logic
is not inherently Windows-specific.

Rationale: Duplication between runtimes is the fastest path to divergence and
regressions in this codebase.

### III. Incremental Change With Explicit Contracts
Refactors and feature work MUST prefer small, reversible steps. Reusable module
boundaries MUST favor typed and explicit contracts over ad-hoc mapping-style
payloads. Temporary facades, compatibility paths, and transition code MUST stay
small, visible, and documented with the intended steady state.

Rationale: The project optimizes for long-term readability and safe evolution,
not large rewrites or implicit coupling.

### IV. Dual-Runtime Safety And Validation
Changes that affect shared behavior, startup wiring, runtime flows, or external
adapters MUST preserve independent execution of both applications: the Discord
bot and the Windows hotkey desktop app. Before closing relevant work,
contributors MUST run appropriate automated checks and MUST call out any
remaining validation gaps explicitly when full validation is not possible.

Rationale: A change is incomplete if it only works for one runtime or silently
breaks startup in the other.

### V. Documentation As Operational Memory
`.specify/` MUST remain the canonical source of project guidance for human and
AI contributors. Durable architecture and operational guides MUST live in
`docs/`, feature execution artifacts MUST live in `specs/`, and documentation
indexes MUST be updated when navigation changes. Repository guidance outside
`.specify/` MUST summarize or link back instead of becoming a second source of
truth.

Rationale: The workflow becomes easier to maintain when governance and
execution standards live in one place and the rest of the repo points back to
it.

## Repository Constraints

- The repository contains two independent applications: Discord bot and Windows
  hotkey desktop app.
- Important entrypoints and ownership anchors:
  - `src/bot.py`
  - `app.py`
  - `src/core/`
  - `src/application/`
  - `src/infrastructure/`
  - `src/presentation/`
  - `src/desktop/`
- Large files are acceptable only when they clearly act as composition roots,
  facades, or orchestration points.
- Cosmetic refactors without a payoff in boundaries, contracts, validation, or
  onboarding clarity SHOULD be rejected.

## Workflow And Review Gates

- Every new feature spec MUST describe user value, affected runtime(s), boundary
  impact, validation approach, and documentation impact.
- Every implementation plan MUST include a constitution check covering clean
  architecture boundaries, shared-logic extraction opportunities, contract
  clarity, bot and desktop validation needs, and documentation updates.
- Every task list MUST include concrete file paths and MUST schedule docs
  updates when architecture, runtime behavior, or contributor guidance changes.
- Reviews MUST prioritize boundary violations, duplicated logic, weak module
  contracts, hidden coupling, stale temporary compatibility code, missing
  validation for either runtime, and stale documentation.

## Governance

This constitution supersedes ad-hoc local process notes for feature planning and
implementation inside the Spec Kit workflow. Canonical repository guidance lives
in `.specify/README.md`, `.specify/memory/constitution.md`, and the templates
under `.specify/templates/`; tool-specific instruction files and docs that
summarize repository policy MUST reference those files instead of restating
divergent rules.

Amendments MUST update this file and any affected templates in `.specify/`. A
MAJOR version bump is required for incompatible governance changes or principle
removals, a MINOR bump is required for new principles or materially expanded
guidance, and a PATCH bump is required for clarifications that do not change the
operating meaning. Compliance reviews for plans, tasks, and code reviews MUST
check the constitution before implementation begins and again before work is
considered done.

**Version**: 1.0.0 | **Ratified**: 2026-04-08 | **Last Amended**: 2026-04-08
