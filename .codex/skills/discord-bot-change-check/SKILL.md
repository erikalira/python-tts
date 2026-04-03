---
name: discord-bot-change-check
description: Validate changes that may impact Discord bot behavior and execution flow.
---

# Canonical references

Read these first:

- `docs/ai/project-context.md`
- `docs/ai/architecture-rules.md`
- `docs/ai/change-playbooks.md`
- `docs/ai/documentation-policy.md`

# When to use

Use when modifying:

- `src/bot.py`
- presentation modules used by the bot
- infrastructure modules used by the bot
- shared logic used by the bot

# Validation flow

1. Identify bot entrypoints, commands, and event listeners touched by the change
2. Check affected dependencies and async flow
3. Confirm shared logic changes did not become Discord-specific
4. Validate bot startup and the changed runtime path
5. Flag docs that should move to `docs/features/` when the change is feature-specific

# Output

- potential break points
- affected commands or events
- manual validation steps
- boundary or shared-logic risks
