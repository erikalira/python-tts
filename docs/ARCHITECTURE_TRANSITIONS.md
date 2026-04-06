# Architecture Transitions

This guide documents how to handle temporary compatibility, facades, and transition code while the repository evolves incrementally.

## Goal

The project prefers small, safe refactors over large rewrites. That means temporary transition structures are acceptable when they:

- protect existing entrypoints
- reduce migration risk
- keep bot and Desktop App working during the change

They should not become invisible permanent architecture.

## What counts as a transition

Typical transition structures include:

- compatibility facades that preserve old imports while code is being split
- fallback paths kept to support existing adapters or runtime scenarios
- temporary bridges between old and new result contracts
- narrow wrappers that preserve behavior while responsibilities are being moved

## Expected behavior

When transition code is introduced, keep it:

- small
- explicit
- local to the affected flow
- easy to remove once callers are migrated

Avoid spreading the same transition logic across multiple modules.

## Steady state

Each temporary transition should have an intended steady state, even if removal does not happen in the same change.

At minimum, contributors should be able to answer:

1. Why does this compatibility path exist?
2. What contract or structure is the long-term target?
3. What needs to migrate before this code can be removed?

## Good examples

- a facade module that re-exports moved use cases while callers migrate
- a temporary fallback kept for older test doubles during a contract change
- a compatibility adapter that protects one runtime while shared logic is extracted

## Bad examples

- leaving mapping-style payload support in multiple layers with no removal plan
- keeping duplicate implementations after all callers already use the new path
- introducing a facade that hides unclear ownership instead of enabling a safe migration

## Removal guidance

Remove transition code when:

- all important callers use the new contract
- tests validate the new path directly
- the compatibility path no longer protects runtime safety or rollout risk

When in doubt, prefer a short follow-up cleanup commit over letting the transition fade into the background.
