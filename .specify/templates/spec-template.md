# Feature Specification: [FEATURE NAME]

**Feature Branch**: `[###-feature-name]`  
**Created**: [DATE]  
**Status**: Draft  
**Input**: User description: "$ARGUMENTS"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - [Brief Title] (Priority: P1)

[Describe this user journey in plain language.]

**Why this priority**: [Explain the value and why it has this priority level.]

**Independent Test**: [Describe how this can be tested independently and which
runtime(s) are involved.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]
2. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 2 - [Brief Title] (Priority: P2)

[Describe this user journey in plain language.]

**Why this priority**: [Explain the value and why it has this priority level.]

**Independent Test**: [Describe how this can be tested independently.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

---

### User Story 3 - [Brief Title] (Priority: P3)

[Describe this user journey in plain language.]

**Why this priority**: [Explain the value and why it has this priority level.]

**Independent Test**: [Describe how this can be tested independently.]

**Acceptance Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected outcome]

## Edge Cases

- What happens when the change affects shared logic consumed by both runtimes?
- How does the system behave when one runtime is intentionally unaffected?
- What happens when configuration, OS bindings, Discord connectivity, or local
  environment state is missing or invalid?
- What temporary compatibility path, if any, is required and when should it be
  removed?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST [specific capability delivered to the user or operator].
- **FR-002**: System MUST identify whether the feature affects the Discord bot,
  the Windows desktop app, or both.
- **FR-003**: System MUST preserve clean architecture boundaries and keep
  business rules out of presentation and infrastructure layers.
- **FR-004**: System MUST avoid duplicating logic between `src/desktop/` and the
  shared modules in `src/`; shared behavior MUST be extracted when reused.
- **FR-005**: System MUST define how the affected runtime path will be validated,
  including startup or smoke checks when relevant.
- **FR-006**: System MUST define required documentation updates when behavior,
  architecture, runtime flow, or contributor guidance changes.

### Key Entities *(include if feature involves data or reusable contracts)*

- **[Entity 1]**: [What it represents, key attributes without implementation.]
- **[Entity 2]**: [What it represents, relationships to other entities.]

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: [Primary user or operator outcome is achieved without breaking the
  unaffected runtime.]
- **SC-002**: [Changed flow can be validated through the stated automated and/or
  manual checks.]
- **SC-003**: [No new duplication is introduced between desktop-specific and
  shared logic.]
- **SC-004**: [Required documentation and guidance are updated and navigable.]

## Assumptions

- [Assumption about target users.]
- [Assumption about scope boundaries.]
- [Assumption about data/environment.]
- [Dependency on existing system/service.]

## Documentation Impact *(mandatory)*

- [List each doc to update in `docs/`, `docs/features/`, `docs/README.md`,
  `README.md`, `AGENTS.md`, or agent-specific instruction files, or state `None`.]
