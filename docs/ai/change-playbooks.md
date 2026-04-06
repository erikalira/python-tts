# Change Playbooks

## Shared logic extraction

Use when similar logic appears in bot flow and desktop flow.

1. Identify the duplicated behavior and its current owners
2. Decide whether it belongs in `core`, `application`, or `infrastructure`
3. Extract the shared unit first
4. Migrate one caller at a time
5. Remove old duplicate code last
6. Validate both entrypoints after the extraction

## Discord bot changes

1. Check `src/bot.py` and any affected presentation or infrastructure modules
2. Confirm command flow, event flow, and async behavior still make sense
3. Verify shared logic changes did not become Discord-specific
4. Validate bot startup and the changed runtime path

## Windows desktop changes

1. Check `app.py`, `src/desktop/app/`, GUI modules, and hotkey-related services
2. Keep blocking work out of GUI event handlers where possible
3. Confirm desktop-specific adapters did not absorb shared business logic
4. Validate startup, input capture, TTS trigger flow, and tray behavior when relevant

## Refactors

1. Classify whether the change is structural only or behavior-changing
2. Split the work into small reversible steps
3. Extract before replacing
4. Replace before deleting
5. Validate bot and desktop startup before closing the refactor
6. Note any temporary facade, compatibility layer, or fallback left behind
7. Prefer closing implicit contracts before doing cosmetic modularization

## Technical leadership heuristics

Use these heuristics when deciding whether a refactor is worth doing:

1. Does it improve boundary integrity?
2. Does it make contracts more explicit?
3. Does it reduce onboarding time for the next contributor?
4. Does it reduce hidden coupling or duplicated policy?
5. Is the benefit large enough to justify the new structure?

If the answer is mostly no, prefer leaving the code alone.

## Reviews

Focus first on:

- boundary violations
- duplication
- weak contracts
- temporary structures that are drifting into permanence
- onboarding clarity of the changed flow
- flow regressions
- missing validation
- stale docs or tool guidance
