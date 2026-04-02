---
name: clean-architecture-review
description: Review changes for clean architecture boundary violations, layer leakage, and misplaced business logic.
---

# When to use

Use this skill when:

- reviewing refactors
- reviewing pull requests
- planning architectural changes
- checking whether code placement matches clean architecture rules
- validating whether a change increased coupling between layers

# Goal

Identify whether the current implementation respects clean architecture boundaries and point out the smallest safe improvements.

# Project layer model

Use this repository layer model:

- `src/core/` → domain rules, entities, value objects, pure business logic
- `src/application/` → use cases, orchestration, application services
- `src/infrastructure/` → external integrations, framework code, IO, persistence, Discord adapters, TTS providers
- `src/presentation/` → entrypoints, controllers, UI-facing flow, request/response handling
- `standalone/` → standalone application-specific runtime and adapters for the Windows hotkey app

# Dependency rules

Apply these rules strictly:

1. `core` must not depend on `application`, `infrastructure`, `presentation`, or `standalone`
2. `application` may depend on `core`, but not on `presentation` or framework-specific runtime code
3. `infrastructure` may depend on `application` and `core`
4. `presentation` should delegate to `application`, not contain business rules
5. `standalone` should only contain app-specific bootstrap/runtime behavior and should reuse shared logic whenever possible
6. business rules must not live in `presentation`, `infrastructure`, or `standalone` unless there is a very strong reason

# What to check

For the relevant files, check the following:

## 1. Layer placement

- Does each file belong in its current layer?
- Is any business logic placed in `presentation`, `infrastructure`, or `standalone`?
- Is orchestration logic in `application` instead of scattered across entrypoints?

## 2. Dependency direction

- Are imports pointing inward correctly?
- Is any inner layer depending on an outer layer?
- Are framework details leaking into core business logic?

## 3. Layer leakage

- Are Discord-specific, GUI-specific, or runtime-specific concerns leaking into `core` or `application`?
- Are concrete implementations being referenced where abstractions/interfaces would be safer?

## 4. Duplication and boundary erosion

- Is similar logic duplicated between `standalone/` and `src/`?
- Did the change introduce shortcut logic in an outer layer instead of reusing a shared use case/service?

## 5. Safe improvements

- What is the smallest safe refactor that improves boundary clarity?
- Which improvements should be done now, and which can be deferred?

# Review process

Follow this process:

1. Identify the changed files and map each file to a layer
2. Inspect imports and dependencies between those files
3. Mark any boundary violations or misplaced logic
4. Separate critical issues from minor improvements
5. Suggest the smallest safe refactor instead of proposing a full rewrite
6. Preserve both application modes:
   - Discord bot
   - Windows standalone hotkey app

# Output format

Return the review using this structure:

## Summary

A short summary of the architectural quality of the change.

## Findings

For each finding, include:

- severity: `critical`, `medium`, or `low`
- file or module
- issue
- why it violates or weakens clean architecture
- recommended fix

## Safe refactor suggestions

List the smallest safe refactors in priority order.

## Validation points

List what should be tested after the change, especially for:

- bot flow
- standalone hotkey flow
- shared services/use cases

# Important behavior

- Prefer incremental refactors over large rewrites
- Do not recommend moving code unless there is a clear architectural reason
- Do not suggest abstractions that add complexity without reducing coupling
- Favor reuse, clarity, and testability
- Preserve current functionality while improving structure
- If the change adds documentation for a new feature, place it under `docs/features/` and keep top-level `docs/` focused on architecture and guides
