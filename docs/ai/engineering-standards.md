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

## Testing and validation

Before finishing relevant code changes:

- run relevant automated tests
- verify imports and boundaries did not break
- confirm Discord bot startup still works
- confirm Windows desktop app startup still works
- test the changed path directly when automated coverage is not enough

## Review expectations

When reviewing or guiding AI changes, prioritize:

- boundary violations
- hidden coupling
- duplicated logic
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
