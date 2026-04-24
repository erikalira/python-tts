## Summary

<!-- What changed and why? Prefer 3-6 lines with product or technical context. -->

## Change Type

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor
- [ ] Documentation
- [ ] Test or validation improvement
- [ ] Performance or reliability

## Architecture Impact

<!-- Explain only what matters for review. -->

- Affected areas:
  - [ ] Discord bot
  - [ ] Windows hotkey desktop app
  - [ ] Shared layers in `src/`
- Runtime summary:
  - [ ] Bot only
  - [ ] Desktop only
  - [ ] Both runtimes
- Architecture notes:
  - Did this change move, extract, or duplicate logic?
  - Were any clean architecture boundaries touched?
  - If desktop-specific code changed, why can it not live in shared code?
- Contracts:
  - [ ] No reusable contract changed
  - [ ] Existing contract changed
  - [ ] New explicit contract introduced
  - Contract notes:
    - `...`
- Compatibility:
  - [ ] No temporary compatibility path
  - [ ] Temporary compatibility path introduced
  - [ ] Temporary compatibility path removed or narrowed
  - Cleanup trigger or intended steady state:
    - `...`

## Validation

<!-- Replace with the concrete checks you actually ran. -->

- Automated checks:
  - `...`
- Manual validation:
  - `...`
- Startup or runtime verification:
  - [ ] Discord bot path validated
  - [ ] Windows desktop app path validated
  - [ ] Not applicable, with reason explained below
- Validation gaps or unrun checks:
  - `...`

## Risks and Review Focus

<!-- Call out the main risks, tradeoffs, or places where reviewers should look closely. -->

- Risk areas:
  - `...`
- Reviewer focus:
  - `...`

## Documentation Impact

- [ ] No documentation update needed
- [ ] Documentation updated in `docs/`
- [ ] Workflow or guidance updated in `.specify/`
- [ ] Derivative instruction files updated (`AGENTS.md`, `.github/`, skills)

<!-- If instructions or governance changed, keep `.specify/` as the source of truth.
Update tool-specific instruction files only to point back to the canonical docs. -->

## Screenshots or Recordings

<!-- Add screenshots, GIFs, or short notes for UI changes when helpful. -->

## Related Issues

<!-- Example: Closes #123 -->

## Notes

<!-- Anything reviewers should know before merging. -->
