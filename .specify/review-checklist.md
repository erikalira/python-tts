# Review Checklist

Use this checklist during code review, self-review, or AI review guidance.

## Core questions

1. Does the change preserve architecture boundaries?
2. Did any file in `src/application/` or `src/presentation/` start importing `src.infrastructure/`?
2. Are module contracts explicit and predictable?
3. Did the change reduce duplication or accidentally introduce more?
4. Is responsibility clearer after the change?
5. Is the changed flow easier for the next contributor to understand?
6. Was a new abstraction introduced for a real repository need, or only because
   a pattern looked appealing?
7. Does the change improve operability, diagnosability, or runtime resilience
   where relevant?
8. Did the author optimize for repository-level maintainability instead of a
   local shortcut?
9. Is the intended steady state clear if compatibility code or a migration path
   was introduced?
10. Was any obsolete path, dead code, or transitional branch left behind
    without a reason?

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
- protocol or interface boundaries that reflect real ownership
- contract docs or naming that make the reusable boundary easy to discover

Watch for:

- direct imports from `src.infrastructure/` into `src/application/` or `src/presentation/`
- implicit dictionaries crossing reusable boundaries
- mapping compatibility left behind without a reason
- hidden assumptions about keys, flags, or shape
- DTOs introduced where no real reusable boundary exists
- domain models carrying transport concerns or presentation-only fields
- interfaces that exist only to satisfy a pattern rather than a repository need

## Service Layer And Ownership

Prefer:

- orchestration in `src/application/`
- thin controllers, command handlers, GUI event handlers, and adapters
- shared policy extracted once instead of duplicated per runtime

Watch for:

- presentation code loading config, picking defaults, or combining business rules
- infrastructure adapters deciding product behavior
- service objects that add indirection without owning meaningful workflow
- large runtime files growing policy they should delegate to shared layers
- ownership that is obvious only after reading multiple files in sequence

## Refactor discipline

Ask:

- was this refactor solving a real maintainability problem?
- was the change kept incremental?
- was any temporary facade or fallback introduced?
- if so, is the intended steady state clear?
- is there a named cleanup point or deletion condition for compatibility code?
- did tests protect the behavior before structure changed?
- did the refactor remove boundary leakage, duplication, or ambiguity?
- did the refactor improve future change cost, not just current aesthetics?

## Reliability And Integration

Check when relevant:

- external calls have explicit timeout behavior
- integration failures return actionable results or messages
- logs help distinguish transport, configuration, and business-rule failures
- bot and desktop failure modes remain understandable to contributors
- compatibility code keeps failure behavior narrow and visible
- observability, transport, or provider integrations enter shared flows through
  contracts or middleware rather than direct adapter imports from inner layers

## Documentation

Update docs when the change affects:

- entrypoints
- runtime behavior
- architecture boundaries
- contributor decision-making
- temporary compatibility structure
- AI guidance hierarchy or repository governance
