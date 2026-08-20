---
name: windows-hotkey-change-check
description: Validate changes that may impact Windows hotkey app behavior and input handling.
---

# Canonical references

Read these first:

- `docs/PROJECT_RULES.md`
- `docs/desktop/DESKTOP_APP_GUIDE.md`
- `docs/architecture/RUNTIME_FLOWS.md`

# When to use

Use when modifying:

- `src/desktop/`
- keyboard input handling
- desktop TTS trigger logic

# Validation flow

1. Identify the impacted desktop entrypoints and runtime modules
2. Validate hotkey capture, text input, and TTS trigger flow
3. Check for blocking work, crashes, or desktop-specific regressions
4. Confirm shared logic changes still fit both runtimes
5. Flag durable docs updates when runtime behavior, contracts, or boundaries
   changed

# Output

- potential break points
- affected input flows
- manual validation checklist
- shared-logic or boundary risks
