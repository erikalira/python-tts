# Engineering Standards

## Change strategy

- Prefer small, incremental refactors
- Make behavior-preserving extractions before larger structural moves
- Remove duplication instead of extending it
- Keep both application modes working after each meaningful step

## Coding standards

- Follow existing project patterns before introducing new ones
- Use type hints in public and shared code
- Choose descriptive names over short clever names
- Keep functions and methods focused on one responsibility
- Add comments only when they explain intent or a non-obvious tradeoff
- Prefer explicit result objects or stable DTO-like shapes over loosely coupled dictionaries across reusable boundaries
- Keep temporary compatibility code small and visible
- Optimize for readability by a future contributor, not only for the current author

## Maintainability expectations

Aim for code that a senior engineer or tech lead would consider easy to extend:

- modules should have clear reasons to change
- composition and runtime wiring should remain understandable
- refactors should reduce ambiguity, not just move code around
- large files are acceptable only when they act as clear roots, facades, or orchestration points

## Testing and validation

Before finishing relevant code changes:

- run relevant automated tests
- default to `tests/unit` for routine validation
- run `tests/integration` explicitly when a change touches real providers, platform bindings, network behavior, or OS-dependent adapters
- do not classify environment-dependent tests as unit tests
- verify imports and boundaries did not break
- confirm Discord bot startup still works
- confirm Windows desktop app startup still works
- test the changed path directly when automated coverage is not enough

## Review expectations

When reviewing or guiding AI changes, prioritize:

- boundary violations
- hidden coupling
- duplicated logic
- weak or implicit contracts between modules
- avoidable compatibility layers that no longer justify their cost
- poor onboarding readability in changed areas
- missing tests for critical paths
- behavior regressions in bot or desktop flow
- stale or conflicting documentation

## Definition of done

A change is not done until:

- implementation is complete
- validation is performed or the remaining gap is called out clearly
- docs are updated when behavior or guidance changed
- the change preserves clean architecture intent
- the repo is easier to evolve than before

When relevant, also call out:

- whether a temporary facade or compatibility path remains
- what the intended steady state is
- whether the changed area became easier for a new contributor to navigate
