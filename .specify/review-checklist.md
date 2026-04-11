# Review Checklist

Use this checklist during code review, self-review, or AI review guidance.

## Core questions

1. Does the change preserve architecture boundaries?
2. Are module contracts explicit and predictable?
3. Did the change reduce duplication or accidentally introduce more?
4. Is responsibility clearer after the change?
5. Is the changed flow easier for the next contributor to understand?

## Runtime safety

Check when relevant:

- Discord bot still has a coherent command and HTTP flow
- Desktop App still has a coherent startup, hotkey, tray, and panel flow
- shared logic did not become runtime-specific by accident

## Contract quality

Prefer:

- typed results
- stable payload shapes
- narrow and intentional adapters

Watch for:

- implicit dictionaries crossing reusable boundaries
- mapping compatibility left behind without a reason
- hidden assumptions about keys, flags, or shape

## Refactor discipline

Ask:

- was this refactor solving a real maintainability problem?
- was the change kept incremental?
- was any temporary facade or fallback introduced?
- if so, is the intended steady state clear?

## Documentation

Update docs when the change affects:

- entrypoints
- runtime behavior
- architecture boundaries
- contributor decision-making
- temporary compatibility structure
