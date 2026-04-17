---
description: "Task list template for feature implementation"
---

# Tasks: [FEATURE NAME]

**Input**: Design documents from `/specs/[###-feature-name]/`  
**Prerequisites**: plan.md (required), spec.md (required for user stories),
research.md, data-model.md, contracts/

**Tests**: Include the tests needed to validate the changed behavior. For this
repository, validation is part of done when a runtime path or shared module is
affected.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Shared domain/application code: `src/core/`, `src/application/`
- Adapters and integrations: `src/infrastructure/`
- Presentation flow: `src/presentation/`
- Desktop runtime and GUI: `src/desktop/`
- Entrypoints: `src/bot.py`, `app.py`
- Tests: `tests/unit/`, `tests/integration/`
- Documentation: `docs/`, `docs/README.md`, `README.md`

## Phase 1: Setup

**Purpose**: Prepare the smallest safe implementation slice

- [ ] T001 Confirm affected modules, runtime(s), and documentation targets from `spec.md` and `plan.md`
- [ ] T002 [P] Add or update scaffolding only where the implementation plan requires it
- [ ] T003 [P] Add targeted tests or validation hooks needed before implementation
- [ ] T004 Capture explicit non-goals, temporary compatibility limits, and validation promises from `plan.md`

---

## Phase 2: Foundations

**Purpose**: Blocking work that enables story delivery without violating the constitution

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Extract or define shared contracts/use cases required across modules
- [ ] T006 [P] Add or adjust adapters/composition wiring required by the chosen architecture path
- [ ] T007 [P] Create or update foundational test coverage for the affected boundary
- [ ] T008 Capture any temporary compatibility path, its intended cleanup point, and its ownership

**Checkpoint**: Foundations ready; user stories can now be implemented safely

---

## Phase 3: User Story 1 - [Title] (Priority: P1)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 1

- [ ] T010 [P] [US1] Add or update unit coverage in `tests/unit/...`
- [ ] T011 [P] [US1] Add integration or startup-path validation in `tests/integration/...` when providers, OS bindings, or runtime wiring change

### Implementation for User Story 1

- [ ] T012 [P] [US1] Implement shared/domain changes in `src/core/...` or `src/application/...`
- [ ] T013 [P] [US1] Implement adapter/runtime changes in the concrete affected files
- [ ] T014 [US1] Wire the story through the correct entrypoint flow without moving business logic into presentation or infrastructure
- [ ] T015 [US1] Add validation, error handling, and typed result contracts where the boundary is reused
- [ ] T016 [US1] Remove or narrow obsolete transitional code that this story makes unnecessary
- [ ] T017 [US1] Update docs and derivative guidance required for this story

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - [Title] (Priority: P2)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 2

- [ ] T018 [P] [US2] Add or update validation needed for this story

### Implementation for User Story 2

- [ ] T019 [P] [US2] Implement the story in the exact affected modules
- [ ] T020 [US2] Integrate with shared services or prior story output without duplicating logic
- [ ] T021 [US2] Update docs required for this story

**Checkpoint**: At this point, User Stories 1 and 2 should both work independently

---

## Phase 5: User Story 3 - [Title] (Priority: P3)

**Goal**: [Brief description of what this story delivers]

**Independent Test**: [How to verify this story works on its own]

### Tests for User Story 3

- [ ] T022 [P] [US3] Add or update validation needed for this story

### Implementation for User Story 3

- [ ] T023 [P] [US3] Implement the story in the exact affected modules
- [ ] T024 [US3] Integrate with existing runtime flows and shared services
- [ ] T025 [US3] Update docs required for this story

**Checkpoint**: All user stories should now be independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] TXXX [P] Final documentation updates in `docs/`, `docs/README.md`, and `README.md`
- [ ] TXXX Sync derivative guidance such as `AGENTS.md` or `.github/copilot-instructions.md` when canonical rules changed
- [ ] TXXX Remove or narrow temporary compatibility code noted in the plan when feasible
- [ ] TXXX Run the promised automated tests
- [ ] TXXX Validate the affected runtime(s): bot startup, desktop startup, or both
- [ ] TXXX Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies, can start immediately
- **Foundations (Phase 2)**: Depends on Setup completion and blocks all stories
- **User Stories (Phase 3+)**: Depend on Foundations completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundations
- **User Story 2 (P2)**: Can start after Foundations and may integrate with US1
- **User Story 3 (P3)**: Can start after Foundations and may integrate with prior stories

### Within Each User Story

- Prefer tests before or alongside implementation for the changed behavior
- Shared/core/application changes before runtime wiring
- Runtime wiring before polish
- Story-specific docs before closing the story
- Story complete before moving to next priority unless the plan states parallel work explicitly

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundations tasks marked [P] can run in parallel
- Once Foundations complete, user stories can proceed in parallel if they do not fight over the same files
- All tests for a user story marked [P] can run in parallel
- Independent file changes within a story marked [P] can run in parallel

## Parallel Example: User Story 1

```text
Task: "Add unit coverage for the shared use case in tests/unit/..."
Task: "Implement shared logic in src/application/..."
Task: "Update desktop wiring in src/desktop/... if it is a different file set"
```

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundations
3. Complete Phase 3: User Story 1
4. Stop and validate User Story 1 independently
5. Demo or release if ready

### Incremental Delivery

1. Complete Setup and Foundations
2. Add User Story 1 and validate it
3. Add User Story 2 and validate it
4. Add User Story 3 and validate it
5. Keep each story independently valuable and safe

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Keep file paths concrete and repo-realistic
- Include docs tasks whenever guidance or behavior changes
- Commit after each task or logical group
- Stop at checkpoints to validate the story independently
- Avoid vague tasks, same-file conflicts, cross-story coupling, or tasks that normalize duplication
