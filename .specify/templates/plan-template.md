# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]  
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See
`.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement, affected runtime(s), and the
smallest architecture-safe approach. Call out the intended steady state if a
temporary migration or compatibility path is required.]

## Technical Context

**Language/Version**: [Python version in use, e.g. Python 3.11+]  
**Primary Dependencies**: [e.g., discord.py, pystray, keyboard, requests, pytest]  
**Storage**: [e.g., environment variables, local config files, transient runtime state, or N/A]  
**Testing**: [e.g., pytest, targeted unit tests, integration tests when adapters/providers are touched]  
**Target Platform**: [Windows desktop app, Discord bot runtime, or both]  
**Project Type**: [two-runtime Python application with shared clean architecture layers]  
**Performance Goals**: [feature-specific latency or responsiveness goals, or N/A]  
**Constraints**: [must preserve clean architecture, avoid desktop/shared duplication, keep both runtimes working]  
**Scale/Scope**: [files/modules/runtimes affected]  
**Affected Runtime(s)**: [bot | desktop | both]  
**Documentation Impact**: [docs to update or `None`]  
**Validation Scope**: [unit, integration, startup smoke checks, manual runtime checks]  
**Risk/Tradeoffs**: [main architectural or runtime risks and the tradeoff accepted]  
**Rollback/Compatibility Plan**: [direct cutover, narrow compatibility path, or `None`]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] Boundary integrity preserved: business logic stays in `src/core/` or
      `src/application/`; dependency direction still points inward.
- [ ] Shared logic plan defined: duplicated behavior between `src/desktop/` and
      shared `src/` modules is avoided or explicitly reduced.
- [ ] Contracts are explicit: reusable boundaries use typed or stable,
      intentional interfaces instead of ad-hoc payloads.
- [ ] Dual-runtime safety addressed: impact on the Discord bot and Windows
      desktop app is identified, including which runtime(s) must be validated.
- [ ] Documentation impact captured: `docs/`, `docs/README.md`, `README.md`,
      and agent guidance updates are identified where relevant.
- [ ] AI guidance sync captured: derivative instruction files and local agent
      assets are identified when canonical `.specify/` guidance changes.
- [ ] Incremental change strategy chosen: the plan favors small, reversible
      steps and explains any temporary compatibility path that remains.
- [ ] Ownership is clear: each changed module has an obvious reason to exist and
      the plan avoids abstraction growth without payoff.
- [ ] Steady state is explicit: obsolete paths to delete, preserve, or narrow
      are identified up front.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- contracts/
`-- tasks.md
```

### Source Code (repository root)

```text
app.py
src/
|-- bot.py
|-- core/
|-- application/
|-- infrastructure/
|-- presentation/
`-- desktop/
    `-- app/

tests/
|-- unit/
`-- integration/

docs/
`-- README.md
```

**Structure Decision**: [Document the exact modules and docs touched by this
feature. Prefer extracting to shared layers instead of adding logic inside
desktop-specific runtime code. Explain why each touched module is the right
owner and note any obsolete path that should be removed or narrowed.]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., temporary compatibility facade] | [current migration need] | [why direct cutover is too risky now] |
| [e.g., desktop-only adapter exception] | [platform constraint] | [why shared placement would be incorrect] |
