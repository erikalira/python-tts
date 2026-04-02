---
name: discord-bot-change-check
description: Validate changes that may impact Discord bot behavior and execution flow.
---

# When to use

Use when modifying:

- bot.py
- services used by the bot
- shared logic used by the bot

# Steps

1. Identify bot entrypoints:
   - bot.py
   - command handlers
   - event listeners

2. Check dependencies:
   - services used by bot
   - external APIs (TTS, Discord API)

3. Validate changes:
   - commands still work
   - events still trigger correctly
   - async flow not broken

4. Check shared logic impact:
   - if moved to shared module, confirm compatibility

5. Validate runtime:
   - bot starts without errors
   - no missing imports

# Output

- potential break points
- affected commands/events
- validation steps to test bot manually
- if the change adds feature documentation, place it in `docs/features/`
