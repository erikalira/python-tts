---
name: desktop-app-gui-ux-review
description: Review or validate Desktop App GUI changes for responsiveness, editability, tray behavior, end-user UX, and clean architecture boundaries.
---

# Canonical references

Read these first:

- `docs/ai/project-context.md`
- `docs/ai/architecture-rules.md`
- `docs/ai/documentation-policy.md`
- `docs/ai/change-playbooks.md`

# When to use

Use when:

- modifying `src/desktop/` GUI code
- changing window, tray, or startup behavior
- adjusting editable fields or form interactions
- reviewing packaging behavior for end users
- validating UX quality before finishing a desktop GUI change

# Goal

Catch UX regressions early while keeping the desktop app responsive, understandable, and aligned with clean architecture.

# What to check

- responsiveness and blocking work in GUI handlers
- editability, focus, typing, paste, and validation flow
- startup, minimize, restore, hide, and tray behavior
- packaging and end-user startup experience
- boundary leakage from GUI code into shared business logic

# Output

Return:

- main UX risks or regressions
- architecture risks if GUI code absorbed business logic
- manual validation checklist for the changed flow
- smallest safe fixes to improve responsiveness or usability
