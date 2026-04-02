---
name: standalone-gui-ux-review
description: Review or validate standalone GUI changes for responsiveness, editability, tray behavior, end-user UX, and clean architecture boundaries.
---

# When to use

Use when:

- modifying `standalone/` GUI code
- changing window, tray, or startup behavior
- adjusting editable fields or form interactions
- reviewing packaging behavior for end users
- validating UX quality before finishing a standalone GUI change

# Goal

Catch UX regressions early while keeping the standalone app responsive, understandable for end users, and aligned with clean architecture.

# What to check

## 1. Responsiveness

- clicks respond consistently
- no obvious freezing during common actions
- long-running work is not executed directly in the GUI event handler
- the interface gives clear feedback during waiting states

## 2. Editability

- text fields can receive focus
- typing, selection, deletion, and paste work normally
- disabled or read-only controls are intentional and visually clear
- validation does not prevent normal editing flow

## 3. Window and tray UX

- startup behavior is intentional and understandable
- minimize, restore, hide, and exit flows are consistent
- tray behavior does not make the app feel lost or unresponsive
- if the app remains in the tray, the user can easily understand how to reopen or quit it

## 4. End-user distribution experience

- the user-facing standalone build should not open an unnecessary terminal window
- packaging decisions match the intended UX for non-technical users
- errors and startup state are communicated clearly without relying on console output

## 5. Architecture boundaries

- GUI code stays in presentation/runtime concerns
- business rules remain in `src/core/` or `src/application/`
- reusable logic is not duplicated between `standalone/` and `src/`
- standalone-specific adapters do not leak into shared business logic

# Review process

1. Identify the standalone entrypoints and GUI files affected by the change
2. Inspect event handlers for blocking work, hidden state changes, or mixed responsibilities
3. Check editable controls and their state transitions
4. Review startup, tray, minimize, restore, and exit behavior
5. Confirm whether the end-user build experience is consistent with a GUI application
6. Cross-check architecture boundaries and duplication with shared logic

# Output

Return:

- main UX risks or regressions
- architecture risks if GUI code absorbed business logic
- manual validation checklist for the changed flow
- smallest safe fixes to improve responsiveness or usability

# Important behavior

- prefer small, safe improvements over large GUI rewrites
- prioritize user-facing reliability over cosmetic tweaks
- do not accept terminal-dependent UX for the distributed GUI app unless explicitly intended
- if a change introduces or updates a GUI behavior, ensure related documentation lives in `docs/features/`
