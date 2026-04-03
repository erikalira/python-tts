---
name: windows-hotkey-change-check
description: Validate changes that may impact Windows hotkey app behavior and input handling.
---

# When to use

Use when modifying:

- `src/desktop/`
- keyboard input handling
- TTS trigger logic

# Steps

1. Identify entrypoints:
   - Desktop App main file
   - hotkey listener

2. Validate input handling:
   - hotkeys still detected
   - no blocking or freezing

3. Check TTS flow:
   - text input still works
   - audio output still triggered

4. Check shared logic:
   - if using extracted services, ensure compatibility

5. Validate runtime:
   - app starts correctly
   - no crashes on key press

# Output

- potential break points
- affected input flows
- manual test checklist
- if the change adds feature documentation, place it in `docs/features/`
