---
name: safe-refactor-plan
description: Generate a safe, step-by-step refactor plan minimizing risk and preserving functionality.
---

# When to use

Use when refactoring code that affects multiple modules, especially shared logic between the Desktop App runtime and the shared layers in `src`.

# Steps

1. Identify impacted areas:
   - files being modified
   - dependencies of these files
   - entrypoints affected (bot.py, app.py)

2. Classify changes:
   - refactor (no behavior change)
   - behavior change (requires validation)

3. Break refactor into small steps:
   - extract function
   - create shared module
   - replace usage incrementally

4. Define validation per step:
   - bot still runs
   - Desktop App still runs
   - no import errors

5. Order steps to minimize risk:
   - extract first
   - replace usage after
   - remove old code last

# Output

- step-by-step plan
- affected files
- validation checklist per step
- documentation placement note when relevant: feature docs go in `docs/features/`, while top-level `docs/` stays for core guides
