---
name: safe-refactor-plan
description: Generate a safe, step-by-step refactor plan minimizing risk and preserving functionality.
---

# Canonical references

Read these first:

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/templates/plan-template.md`
- `.specify/review-checklist.md`
- `docs/ARCHITECTURE_TRANSITIONS.md`

# When to use

Use when refactoring code that affects multiple modules, especially shared logic
between the desktop runtime and the shared layers in `src`.

# Planning flow

1. Identify impacted files, imports, and entrypoints
2. Classify whether the work is structural only or behavior-changing
3. Break the refactor into small reversible steps
4. Define validation for each step
5. Order the work to extract first, replace second, remove old code last
6. Prefer tightening contracts before broad modularization when both are needed
7. Call out any temporary facade or compatibility layer that will remain after the plan

# Output

- step-by-step plan
- affected files
- validation checklist per step
- documentation note when relevant

The plan should optimize for:

- explicit contracts
- reduced hidden coupling
- easier onboarding in the changed area
- smaller future maintenance cost, not just cleaner file layout
