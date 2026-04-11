# Transition Cleanup Rule

Use this rule whenever temporary compatibility, facades, or fallback paths are
introduced.

## Rule

Temporary transition code is acceptable only when it protects a migration in
progress.

It should not remain in the codebase without a visible reason.

## Minimum expectation

For each temporary transition, be able to answer:

1. What does this transition protect?
2. What is the intended steady state?
3. What needs to migrate before cleanup?

## Good timing for cleanup

Remove the transition when:

- the main callers already use the new contract
- tests validate the new path directly
- the old path no longer reduces rollout risk

## Warning signs

The transition is probably overstaying when:

- new code keeps using the compatibility path by default
- nobody can explain why it still exists
- it appears in more than one layer
- it makes module contracts harder to understand

## Recommended practice

- keep the transition narrow
- keep the steady state documented
- prefer a short cleanup follow-up over leaving it ambiguous
