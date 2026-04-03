---
name: shared-logic-extraction
description: Identify duplicated logic between the Desktop App runtime and the shared layers in `src`, then extract it into shared use cases or services.
---

# Canonical references

Read these first:

- `docs/ai/project-context.md`
- `docs/ai/architecture-rules.md`
- `docs/ai/change-playbooks.md`
- `docs/ai/documentation-policy.md`

# When to use

Use when similar logic exists in multiple flows, especially the Discord bot and desktop app.

# Extraction flow

1. Identify duplicated behavior, rules, or external-call orchestration
2. Classify the target layer: `core`, `application`, or `infrastructure`
3. Extract the shared module or interface
4. Replace duplicate call sites incrementally
5. Validate both entrypoints after the extraction

# Output

- duplicated areas
- extraction plan
- target location
- validation notes
