---
name: shared-logic-extraction
description: Identify duplicated logic between the Desktop App runtime and the shared layers in `src`, then extract it into shared use cases or services.
---

# When to use

Use when similar logic exists in multiple flows (Discord bot and Windows app).

# Steps

1. Identify duplicated logic:
   - same function behavior
   - same business rules
   - same external calls

2. Classify logic:
   - business → move to `core` or `application`
   - integration → move to `infrastructure`
   - UI/entrypoint → keep separate

3. Extract shared module:
   - create use case or service
   - define interface if needed

4. Replace duplicated code with shared usage

# Output

- duplicated areas
- extraction plan
- target location (core/application/infrastructure)
- if documentation is added for the extracted feature or refactor outcome, use `docs/features/`
