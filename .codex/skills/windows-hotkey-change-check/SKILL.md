---
name: windows-hotkey-change-check
description: Validate changes that may impact Windows hotkey app behavior and input handling.
---

# Canonical references

Read these first:

- `docs/ai/project-context.md`
- `docs/ai/architecture-rules.md`
- `docs/ai/change-playbooks.md`
- `docs/ai/documentation-policy.md`

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
5. Call out feature docs that belong in `docs/features/`

# Output

- potential break points
- affected input flows
- manual validation checklist
- shared-logic or boundary risks
