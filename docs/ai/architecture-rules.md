# Architecture Rules

## Clean architecture model

- `core` must stay pure and framework-agnostic
- `application` coordinates domain behavior and use cases
- `infrastructure` implements external concerns and adapters
- `presentation` handles requests, commands, and UI-facing flow
- `src/desktop` contains desktop-specific runtime and adapters only

## Dependency direction

Apply these rules strictly:

1. `src/core/` must not depend on `src/application/`, `src/infrastructure/`, `src/presentation/`, or `src/desktop/`
2. `src/application/` may depend on `src/core/`, but not on framework-specific runtime code
3. `src/infrastructure/` may depend on `src/application/` and `src/core/`
4. `src/presentation/` should delegate to `src/application/` and avoid business rules
5. `src/desktop/` should reuse shared logic from `src/` whenever possible instead of reimplementing it

## Strict project rules

- Never duplicate logic between `src/desktop/` and shared modules in `src/`
- Never place business logic in presentation or infrastructure unless there is a strong and explicit reason
- Prefer extracting interfaces, use cases, or services instead of copying behavior
- Preserve independent execution of the Discord bot and Windows app
- Prefer explicit typed contracts at module boundaries over ad-hoc mappings when the boundary is reused
- Keep temporary facades and compatibility paths narrow, intentional, and easy to remove

## Preferred placement

- Domain rules, validation rules, and business decisions -> `src/core/` or `src/application/`
- Coordination across services and flows -> `src/application/`
- Discord, HTTP, TTS, filesystem, config persistence, and framework details -> `src/infrastructure/`
- Slash commands, controllers, and GUI event wiring -> `src/presentation/` or desktop runtime adapters
- Windows-specific tray, hotkey runtime, packaging behavior, and GUI integration -> `src/desktop/`

## Common anti-patterns

- Use cases instantiating concrete infrastructure directly
- GUI or command handlers embedding business decisions
- Desktop runtime reimplementing shared routing or validation logic that belongs in `src/`
- Infrastructure modules becoming the place where product rules live
- Shared policy copied into multiple instruction files and drifting over time
- Compatibility shims becoming permanent architecture by inertia
- Large modules that mix composition, business flow, presentation mapping, and transport details without a clear reason

## Scalability guidance

For this project, good scalability means:

- both runtimes can evolve without duplicating shared rules
- contributors can find the relevant flow quickly
- modules expose predictable contracts and responsibilities
- composition roots stay readable even when they remain large

Do not split files only because they are long. Split when doing so improves responsibility boundaries, contract clarity, onboarding readability, or change isolation.
