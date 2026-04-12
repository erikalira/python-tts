# Engineering References

This file records the books and software design references that inform the
engineering direction of this repository.

It is intentionally not a second source of truth for repository rules.
Project-specific operating guidance still lives in `.specify/`. This file exists
to preserve context about the ideas the project values and how they translate
into practical decisions here.

## How To Use This Document

- Use this file to understand the architectural taste behind the repository.
- Use `.specify/memory/constitution.md` for binding principles.
- Use `.specify/review-checklist.md` for actionable review questions.
- Prefer project-specific rules over generic book vocabulary when making code
  changes.

## Core References And Their Practical Impact

### The Pragmatic Programmer

Important concepts for this repo:

- remove duplication before it spreads across bot and desktop runtimes
- prefer automation and fast feedback for validation
- keep code easy to change rather than clever
- treat architecture as an everyday design activity

Applied here:

- incremental refactors backed by tests
- shared logic extraction from runtime-specific code
- contributor-friendly code and docs over clever indirection

### Clean Code

Important concepts for this repo:

- explicit naming
- single-purpose functions and modules
- readable flow boundaries
- minimizing hidden assumptions

Applied here:

- clear use-case and DTO names
- smaller presentation responsibilities
- refactors that improve ownership and onboarding clarity

### Refactoring

Important concepts for this repo:

- improve design without changing behavior
- move in small, safe steps
- use tests as a safety net
- remove duplication and misplaced responsibilities deliberately

Applied here:

- extracting DTOs at boundaries
- moving border logic into application services
- preserving dual-runtime behavior during design cleanup

### Unit Testing

Important concepts for this repo:

- test behavior, not incidental structure
- protect refactors with focused tests
- keep adapters and use cases easy to exercise in isolation

Applied here:

- use-case tests
- presenter/controller tests
- desktop and bot flow tests around integration boundaries

### Grokking Algorithms

Important concepts for this repo:

- understanding simple data structures clearly before optimizing
- queues and ordered processing
- dictionary-style lookups and pragmatic state indexing
- basic algorithmic trade-offs between clarity and efficiency

Applied here:

- audio queue behavior and processing order
- voice catalog and runtime lookup flows
- reasoning about per-guild and per-member state maps
- preferring simple, understandable algorithms unless scale proves otherwise

### Head First Design Patterns

Important concepts for this repo:

- use patterns as vocabulary, not decoration
- adapter and strategy patterns are often enough
- avoid pattern-heavy code when simpler code is clearer

Applied here:

- adapters around runtime-specific integrations
- strategy-like runtime selection for TTS engines
- caution against introducing patterns without payoff

### HTTP: The Definitive Guide

Important concepts for this repo:

- request/response boundaries are contracts
- status codes and error messages matter
- transport concerns should stay separate from business logic

Applied here:

- HTTP controllers and presenters
- desktop-to-bot HTTP integration
- explicit handling of health checks, timeouts, and status codes

### Fundamentals Of Software Architecture

Important concepts for this repo:

- architecture is trade-offs
- boundaries matter more than purity theater
- coupling, cohesion, and operability are first-class concerns

Applied here:

- practical clean architecture boundaries
- avoiding overengineering when a simpler model is enough
- favoring maintainability across two independent runtimes

### Clean Architecture

Important concepts for this repo:

- dependencies point inward
- use cases own application behavior
- infrastructure and UI should delegate
- contracts between layers should stay explicit

Applied here:

- `src/core/`, `src/application/`, `src/infrastructure/`, `src/presentation/`
- desktop runtime code delegating to shared application logic where possible
- boundary protection in reviews and refactors

### Learning Domain-Driven Design

Important concepts for this repo:

- distinguish entities, value objects, DTOs, and services
- use a shared language for important concepts
- avoid mixing transport models with internal models

Applied here:

- DTO extraction at application boundaries
- clearer naming around TTS requests, voice context, and desktop bot flows
- keeping the domain lean unless richer behavior removes duplication

### Designing Data-Intensive Applications

Important concepts for this repo:

- explicit trade-offs around reliability and correctness
- understanding system behavior under failure
- care with state, queues, and concurrency

Applied here:

- audio queue behavior and runtime coordination
- caution around failure visibility and state transitions

This is more of a conceptual influence than an immediate pattern source for the
current repository.

### Enterprise Integration Patterns

Important concepts for this repo:

- adapters and translators at system boundaries
- request/reply and message-shape clarity
- anti-corruption thinking between subsystems

Applied here:

- desktop app talking to the bot over HTTP
- translation between runtime-specific payloads and application DTOs
- preserving clean seams around integration code

### Release It!

Important concepts for this repo:

- timeouts and partial failures are normal
- resilience must be designed in, not added later
- health checks and graceful degradation matter

Applied here:

- bot health endpoint usage
- timeout handling in desktop-to-bot integration
- explicit runtime availability checks for voice dependencies

### Software Architecture: The Hard Parts

Important concepts for this repo:

- some architecture decisions are about trade-offs, not ideals
- distributed failure and boundary ownership need explicit thinking

Applied here:

- deciding where shared logic belongs
- balancing runtime independence with shared code reuse

### Building Evolutionary Architectures

Important concepts for this repo:

- evolve architecture with guardrails
- improve structure incrementally
- encode design intent into repeatable checks

Applied here:

- constitution and review checklist updates
- gradual DTO/service-layer adoption instead of rewrite-driven cleanup

### Observability Engineering

Important concepts for this repo:

- logs and signals should explain behavior, not just record events
- operational clarity is part of system design

Applied here:

- structured runtime logging
- surfacing meaningful integration failures
- keeping failure modes diagnosable for both bot and desktop flows

## Concepts The Repository Intentionally Applies

These concepts are considered especially valuable for the current codebase:

- layered architecture
- service-layer orchestration
- repository abstractions where they reduce coupling
- DTOs at reusable boundaries
- incremental refactoring with test protection
- explicit runtime failure handling
- narrow adapters and translators at integration seams
- practical observability for runtime and integration flows

## Concepts To Apply Carefully

These ideas are useful, but can easily become overengineering if forced:

- rich domain models for simple flows
- data-mapper-style indirection without real persistence complexity
- pattern-heavy abstractions that do not reduce duplication or leakage
- architecture purity that makes the code harder to understand

## Notes On Book Names

The project keeps book titles here for contributor context, but not in the
constitution or review checklist. Repository rules should stay actionable and
project-specific even when their design taste is inspired by broader software
engineering literature.
