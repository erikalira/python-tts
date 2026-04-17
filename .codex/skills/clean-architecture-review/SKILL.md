---
name: clean-architecture-review
description: Review changes for clean architecture boundary violations, layer leakage, and misplaced business logic.
---

# Canonical references

Read these first:

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/review-checklist.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_TRANSITIONS.md`

# When to use

Use this skill when:

- reviewing refactors
- reviewing pull requests
- planning architectural changes
- checking whether code placement matches clean architecture rules
- validating whether a change increased coupling between layers

# Goal

Identify whether the implementation respects project boundaries and recommend the
smallest safe improvement. Also assess whether the changed area improves
explicit contracts, onboarding readability, and temporary-structure discipline.

# Review process

1. Identify the changed files and map each file to a layer
2. Inspect imports and dependencies between those files
3. Mark any boundary violations, layer leakage, or duplicated logic
4. Note weak contracts, lingering mapping-style payloads, or compatibility
   layers that may no longer be justified
5. Separate critical issues from minor improvements
6. Suggest the smallest safe refactor instead of a full rewrite
7. Preserve both execution modes:
   - Discord bot
   - Windows desktop app

# Output format

## Summary

A short summary of the architectural quality of the change.

## Findings

For each finding include:

- severity: `critical`, `medium`, or `low`
- file or module
- issue
- why it weakens clean architecture
- recommended fix

Prefer calling out:

- hidden coupling
- unclear ownership of responsibilities
- temporary facades that should remain temporary
- poor readability for the next contributor in the affected flow

## Safe refactor suggestions

List the smallest safe refactors in priority order.

## Validation points

List what should be tested after the change, especially for:

- bot flow
- desktop app hotkey flow
- shared services and use cases
