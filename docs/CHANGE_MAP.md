# Change Map

This guide helps contributors decide where to start when changing the project.

It is intentionally short. The goal is to reduce exploration time, not to document every file.

## Start here first

When you pick up a change:

1. identify which runtime is affected
2. identify whether the change is shared or runtime-specific
3. open the entrypoint and composition root for that flow
4. find the first shared use case or runtime coordinator involved

## If the change is in the Discord bot

Start with:

- `src/bot.py`
- `src/bot_runtime/container.py`
- `src/presentation/discord_commands.py`
- `src/presentation/http_controllers.py`

Then decide:

- command behavior or transport mapping:
  start in `src/presentation/`
- shared orchestration or rules:
  move into `src/application/`
- Discord-specific adapters or runtime wiring:
  use `src/infrastructure/` or `src/bot_runtime/`

## If the change is in the Desktop App

Start with:

- `app.py`
- `src/desktop/app/bootstrap.py`
- `src/desktop/app/desktop_app.py`

Then decide:

- GUI behavior:
  start in `src/desktop/gui/`
- runtime coordination:
  start in `src/desktop/app/`
- hotkeys, tray, local TTS, notifications:
  start in `src/desktop/services/` or `src/desktop/adapters/`
- shared orchestration or reusable logic:
  prefer `src/application/`

## If the change is shared between bot and desktop

Start with:

- `src/application/`
- `src/core/`

Use `src/desktop/` or `src/presentation/` only for runtime-specific entry and exit points.

Good candidates for shared logic:

- validation rules
- flow orchestration
- result contracts
- routing decisions
- reusable interfaces

## If the change is a refactor

Start with:

- `docs/ai/change-playbooks.md`
- `docs/ARCHITECTURE_TRANSITIONS.md`
- the current composition root or use case involved

Prefer:

- extract before replace
- replace before delete
- typed contracts before cosmetic file splitting

## If the change is mostly onboarding or docs

Start with:

- `README.md`
- `docs/README.md`
- `docs/ARCHITECTURE.md`
- `docs/RUNTIME_FLOWS.md`

Update docs when the change affects:

- entrypoints
- runtime behavior
- architecture boundaries
- temporary compatibility structure
- contributor decision-making

## If you are unsure where code belongs

Use this rule of thumb:

- pure rule or reusable decision:
  `src/core/` or `src/application/`
- transport, framework, filesystem, network, tray, Discord client, HTTP server:
  `src/infrastructure/` or `src/desktop/`
- command/controller/UI event flow:
  `src/presentation/` or `src/desktop/gui/`

If a piece of logic might be needed by both runtimes later, bias toward shared layers instead of duplicating it in desktop-only code.
