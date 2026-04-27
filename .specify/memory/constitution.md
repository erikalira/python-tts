<!--
Sync Impact Report
- Version change: 1.2.1 -> 1.3.0
- Modified principles:
  - V. Documentation As Operational Memory -> V. Documentation As Operational Memory
- Added sections:
  - Repository Language Policy
- Removed sections:
  - None
- Templates requiring updates:
  - updated: .specify/README.md
  - updated: .specify/memory/ai-pitfalls.md
  - updated: .specify/review-checklist.md
  - updated: .specify/templates/agent-file-template.md
  - updated: AGENTS.md
  - updated: .github/copilot-instructions.md
  - updated: .github/copilot-workspace.yml
  - updated: .github/instructions/documentation-organization.md
  - updated: .specify/sync-report-template.md
  - not required: .specify/templates/plan-template.md
  - not required: .specify/templates/spec-template.md
  - not required: .specify/templates/tasks-template.md
  - not required: docs/README.md
  - not required: README.md
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

Direct imports from `src.infrastructure/` into `src/application/` or
`src/presentation/` MUST be treated as architecture blockers unless the file is
an explicitly documented composition root or runtime bootstrap module outside
those layers. Shared logic MUST depend on contracts defined inward, not on
concrete adapters.

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
small, visible, and documented with the intended steady state. Contributors MUST
prefer deleting obsolete paths once the replacement is safe over normalizing
permanent dual-path complexity.

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
truth. Agent- or tool-specific instruction files MUST stay derivative and MUST
be synchronized when canonical guidance changes.

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

## Repository Language Policy

All repository code, comments, documentation, specifications, tests, commit
messages, pull request descriptions, and AI-generated project artifacts MUST be
written in English by default.

User-facing runtime text MAY use another language only when a feature explicitly
requires localization, language-specific behavior, or a locale fixture. Such
exceptions MUST stay scoped to the user-facing surface or test fixture that
needs them.

## Workflow And Review Gates

- Every new feature spec MUST describe user value, affected runtime(s), boundary
  impact, validation approach, and documentation impact.
- Every implementation plan MUST include a constitution check covering clean
  architecture boundaries, shared-logic extraction opportunities, contract
  clarity, module ownership, steady-state intent, bot and desktop validation
  needs, and documentation updates.
- Every task list MUST include concrete file paths and MUST schedule docs
  updates when architecture, runtime behavior, or contributor guidance changes.
- Reviews MUST prioritize boundary violations, duplicated logic, weak module
  contracts, hidden coupling, stale temporary compatibility code, missing
  validation for either runtime, stale documentation, and abstractions that add
  ceremony without reducing repository risk.
- Reviews and implementation checks MUST explicitly ask whether any file in
  `src/application/` or `src/presentation/` newly imports `src.infrastructure/`;
  if yes, the change SHOULD be blocked until that dependency is removed or the
  owning module is moved to an appropriate runtime/composition layer.

## Decision Standard For Humans And AI

Contributors MUST make decisions the way a strong senior or staff engineer
would for this repository: optimize for the long-term cost of change across the
whole codebase, not for local convenience in one file or one runtime.

- The preferred solution is usually the smallest architecture-safe step that
  improves boundaries, contracts, readability, or runtime safety.
- New abstractions MUST be justified by a concrete repository problem such as
  duplication, ownership confusion, change friction, or resilience gaps.
- Large reorganizations SHOULD be rejected unless they remove a concrete source
  of recurring risk that smaller steps cannot address.
- Plans and reviews SHOULD make tradeoffs, non-goals, and rollout or cleanup
  expectations explicit rather than relying on implied intent.
- Onboarding clarity for the next contributor MUST be treated as part of the
  engineering outcome, not just documentation polish.

## Governance

This constitution supersedes ad-hoc local process notes for feature planning and
implementation inside the Spec Kit workflow. Canonical repository guidance lives
in `.specify/README.md`, `.specify/memory/constitution.md`, and the templates
under `.specify/templates/`; tool-specific instruction files and docs that
summarize repository policy MUST reference those files instead of restating
divergent rules.

Amendments MUST update this file and any affected templates in `.specify/`. A
MAJOR version bump is required for incompatible governance changes or principle
removals, a MINOR version bump is required for new principles or materially
expanded guidance, and a PATCH version bump is required for clarifications that
do not change the operating meaning. Compliance reviews for plans, tasks, and
code reviews MUST check the constitution before implementation begins and again
before work is considered done.

## Instruction Hierarchy And Sync Discipline

`.specify/` is the repository's guidance authority for humans and AI agents.
Derivative files such as `AGENTS.md`, `.github/copilot-instructions.md`,
`.github/copilot-workspace.yml`, `.github/instructions/*.md`, and
project-specific skill summaries MUST not silently diverge from it.

- If canonical guidance changes, derivative instruction files MUST be reviewed
  and updated in the same change when relevant.
- Tool-specific files SHOULD summarize only the most actionable repository
  constraints and link back to `.specify/` for the full rule set.
- New durable AI guidance SHOULD be added to `.specify/` first, then propagated
  outward only as concise derivative summaries.
- Stale references to retired guidance locations or alternate canonical sources
  MUST be removed instead of left as historical clutter.

## Project-Specific Guidance Locations

The repository may include tool-specific agent assets, but they are derivative
unless this constitution explicitly says otherwise.

- `.agents/` contains agent-facing workflows and Spec Kit skills.
- `.codex/` contains Codex skills, domain review playbooks, and local
  architecture checks.
- `.github/` contains GitHub and Copilot-facing summaries, templates, and
  automation wiring.

These locations MUST reference `.specify/` as the authority when they encode
repository policy. They MAY contain tool-specific execution details, but they
MUST NOT redefine architecture, documentation, validation, or governance rules
in a way that conflicts with `.specify/`.

## Instruction File Maintenance

Instruction and governance Markdown files MUST be maintained as operational
artifacts, not informal notes.

- Markdown in `.specify/` SHOULD use consistent headings, checklist syntax, and
  relative links that work from the file location.
- Derivative instruction files MUST link back to `.specify/` and identify the
  constitution version they summarize.
- Derivative instruction files SHOULD include a last-synced date when they are
  manually maintained.
- Canonical instruction files SHOULD identify their main derivative consumers
  when that helps future synchronization.
- New durable instruction files MUST be added to the governance or docs index
  that makes them discoverable.

## Constitution Sync Checklist

When `constitution.md` changes, the same change SHOULD review and update the
following files where relevant. Use `.specify/sync-report-template.md` for a
durable report when the update spans multiple files.

- [ ] `AGENTS.md`
- [ ] `.github/copilot-instructions.md`
- [ ] `.github/copilot-workspace.yml`
- [ ] `.github/instructions/*.md`
- [ ] `.agents/` and `.codex/` project-specific skills or summaries
- [ ] `.specify/templates/*`
- [ ] `.specify/README.md`
- [ ] `.specify/review-checklist.md`
- [ ] `docs/README.md` if navigation changes
- [ ] `README.md` if governance or contributor entrypoints change

Current sync target: constitution v1.3.0. Update status: DONE.

## Architecture And Design Heuristics

The repository SHOULD prefer practical application of proven software design
concepts when they clarify boundaries, reduce change risk, or improve
operability. These heuristics guide decisions without forcing ceremony for its
own sake.

- Layered architecture SHOULD remain the default mental model for cross-module
  changes.
- Service-layer orchestration SHOULD live in `src/application/` rather than in
  controllers, GUI handlers, or infrastructure adapters.
- Repository-style abstractions SHOULD be used when they decouple shared
  application logic from infrastructure or external systems.
- DTOs SHOULD be introduced at reusable boundaries when they make contracts
  clearer than passing implicit dictionaries or mixed-purpose models.
- Domain models MAY stay lean when the behavior is simple; richer domain
  behavior SHOULD be introduced only when it removes duplicated policy or
  scattered invariants.
- Data-mapper-style indirection SHOULD NOT be introduced unless persistence
  complexity justifies it.

## Reliability And Runtime Resilience

Shared flows, bot HTTP endpoints, desktop integrations, and background runtime
behavior SHOULD be designed with failure handling in mind.

- External calls SHOULD define timeout behavior explicitly.
- Partial failures SHOULD produce actionable typed results or user-facing
  messages rather than silent fallbacks.
- Health checks, startup validation, and dependency-availability checks SHOULD
  remain explicit and easy to diagnose.
- Logging SHOULD help contributors distinguish configuration issues, transport
  failures, voice-runtime failures, and business-rule failures.
- Temporary compatibility or migration code MUST keep its failure modes narrow
  and observable.

## Evolution And Refactoring Discipline

The codebase SHOULD evolve through small architectural improvements backed by
tests and local validation.

- Refactors SHOULD preserve behavior while improving naming, ownership,
  contracts, or shared reuse.
- New abstractions SHOULD be introduced only when they remove duplication,
  shrink boundary leakage, or improve operability.
- Pattern usage MUST be justified by a concrete repository problem; pattern
  hunting without payoff SHOULD be rejected.
- Architecture decisions SHOULD prefer reversible, incremental steps over large
  rewrites.
- New durable guidance SHOULD be encoded as project-specific rules or checklists
  instead of book quotations or theory-heavy summaries.

**Version**: 1.3.0 | **Ratified**: 2026-04-08 | **Last Amended**: 2026-04-27
