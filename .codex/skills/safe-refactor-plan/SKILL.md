---
name: safe-refactor-plan
description: Generate a safe, step-by-step refactor plan minimizing risk and preserving functionality.
---

# Canonical references

Read these first:

- `docs/ai/project-context.md`
- `docs/ai/architecture-rules.md`
- `docs/ai/engineering-standards.md`
- `docs/ai/change-playbooks.md`

# When to use

Use when refactoring code that affects multiple modules, especially shared logic between the desktop runtime and the shared layers in `src`.

# Planning flow

1. Identify impacted files, imports, and entrypoints
2. Classify whether the work is structural only or behavior-changing
3. Break the refactor into small reversible steps
4. Define validation for each step
5. Order the work to extract first, replace second, remove old code last

# Output

- step-by-step plan
- affected files
- validation checklist per step
- documentation note when relevant
