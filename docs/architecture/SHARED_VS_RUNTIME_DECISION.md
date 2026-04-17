# Shared Vs Runtime-Only Decision Guide

Use this guide when deciding whether code should live in shared layers under
`src/` or stay runtime-specific in the Discord bot or Desktop App flows.

This is a durable decision aid, not the canonical governance source. For binding
rules, use `.specify/memory/constitution.md`.

## Default Rule

If a behavior can reasonably be reused by both runtimes, bias toward shared
layers in `src/core/` or `src/application/`.

Keep code runtime-specific only when it is truly tied to:

- Windows GUI, tray, keyboard hooks, or local OS behavior
- Discord transport, Discord client lifecycle, or HTTP transport wiring
- concrete provider, framework, or toolkit details that should not leak inward

## Fast Decision Questions

Ask these in order:

1. Is this rule or workflow inherently about Discord, Windows, Tkinter, HTTP,
   tray, hotkeys, or another platform concern?
2. If I removed the framework or runtime detail, would the behavior still make
   sense as shared application logic?
3. Could the other runtime need the same decision, validation, routing, or
   orchestration soon?
4. Am I putting this in `src/desktop/` or a bot-specific module just because it
   is the first place I touched?
5. Would placing it in shared layers reduce duplication or clarify ownership?

If the answer to `2`, `3`, or `5` is yes, shared placement is usually the right
default.

## Good Shared Candidates

- validation rules
- routing decisions
- orchestration across interfaces
- reusable typed result contracts
- policy about fallback, selection, or status aggregation
- shared use cases that both runtimes can call

Typical homes:

- `src/core/` for pure rules, entities, and interfaces
- `src/application/` for workflows, DTOs, and orchestration

## Good Runtime-Only Candidates

- Tkinter windows, widgets, tray behavior, focus/edit interactions
- keyboard capture and Windows-specific input handling
- Discord client events, guild/channel wiring, and transport-specific adapters
- HTTP server setup or request parsing at the transport boundary
- provider setup that is meaningful only for one runtime

Typical homes:

- `src/desktop/` for Desktop App runtime and GUI concerns
- `src/presentation/` for entry/exit flow concerns
- `src/infrastructure/` for concrete external integrations

## Smells That Say "Move This To Shared"

- the same rule appears in both bot and desktop code
- a runtime module starts accumulating business decisions
- a GUI handler or controller is combining validation, defaults, and workflow
- a contract or status shape is being redefined in multiple places
- the only reason a function is runtime-specific is historical placement

## Smells That Say "Keep This Runtime-Specific"

- the code is mostly framework API calls with little reusable policy
- moving it to shared layers would force framework or toolkit concepts inward
- the behavior exists only to translate between a concrete API and a shared
  contract
- the code would become less readable if extracted only for pattern purity

## Practical Rule Of Thumb

Prefer extracting shared policy first, then leave only thin runtime adapters at
the edges.

Good shape:

- runtime collects input
- shared layer decides what should happen
- runtime adapter performs concrete side effects

Risky shape:

- runtime layer decides policy
- shared layer becomes a passive helper
- the next runtime reimplements the same flow differently
