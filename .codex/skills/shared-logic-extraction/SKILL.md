---
name: shared-logic-extraction
description: Identify duplicated logic between the Desktop App runtime and the shared layers in `src`, then extract it into shared use cases or services.
---

# Canonical references

Read these first:

- `.specify/README.md`
- `.specify/memory/constitution.md`
- `.specify/review-checklist.md`
- `docs/ARCHITECTURE.md`
- `docs/RUNTIME_FLOWS.md`

# When to use

Use when similar logic exists in multiple flows, especially the Discord bot and
desktop app.

# Extraction flow

1. Identify duplicated behavior, rules, or external-call orchestration
2. Classify the target layer: `core`, `application`, or `infrastructure`
3. Extract the shared module or interface
4. Replace duplicate call sites incrementally
5. Validate both entrypoints after the extraction
6. Prefer stable contracts and clear ownership over thin shared helpers with vague responsibility
7. If a compatibility facade is left behind, describe the intended end state

# Output

- duplicated areas
- extraction plan
- target location
- validation notes

Good extractions should leave the repo:

- easier to navigate
- more explicit at module boundaries
- less dependent on historical knowledge from the original author
