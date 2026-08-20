# Project Rules

Binding rules for this repository. Everything here is specific to this codebase:
generic engineering practice lives in the agent definitions, and change workflow
lives in OpenSpec.

## Two runtimes

This repository ships two independent applications that must keep working
independently after any change:

- Discord bot — entrypoint `src/bot.py`
- Windows hotkey desktop app — entrypoint `app.py`

A change is incomplete if it only works for one runtime or silently breaks
startup in the other.

## Architecture boundary (hard rule)

Dependencies flow inward across `src/core/`, `src/application/`,
`src/infrastructure/`, `src/presentation/`, and `src/desktop/`.

- `src/application/` and `src/presentation/` MUST NOT import
  `src.infrastructure` directly. Treat a new import as a blocker.
- If shared logic needs infrastructure behavior, define a contract inward and
  bind the concrete adapter in a composition root or runtime bootstrap module.
- Business rules live in `src/core/` or `src/application/`. Presentation,
  runtime, and infrastructure code delegates instead of absorbing product policy.
- `src/desktop/` is a Windows-specific runtime, not a second shared application
  layer. Behavior reused by both runtimes gets extracted into shared interfaces,
  use cases, or services before copy-paste is introduced or expanded.

## Where to start a change

**Discord bot** — `src/bot.py`, `src/bot_runtime/container.py`,
`src/presentation/discord_commands.py`, `src/presentation/http_controllers.py`.
Command behavior and transport mapping stay in `src/presentation/`; shared
orchestration moves to `src/application/`; Discord adapters and wiring go in
`src/infrastructure/` or `src/bot_runtime/`.

**Desktop app** — `app.py`, `src/desktop/app/bootstrap.py`,
`src/desktop/app/desktop_app.py`. GUI behavior in `src/desktop/gui/`; runtime
coordination in `src/desktop/app/`; hotkeys, tray, local TTS and notifications in
`src/desktop/services/` or `src/desktop/adapters/`.

**Shared between both** — `src/application/use_cases.py` for the stable public
use-case imports, then `src/application/` and `src/core/`. Validation rules, flow
orchestration, result contracts, routing decisions and reusable interfaces belong
here rather than duplicated per runtime.

**Unsure where code belongs:**

| Kind of logic | Home |
| --- | --- |
| Pure rule or reusable decision | `src/core/` or `src/application/` |
| Transport, framework, filesystem, network, tray, Discord client, HTTP server | `src/infrastructure/` or `src/desktop/` |
| Command / controller / UI event flow | `src/presentation/` or `src/desktop/gui/` |

If logic might be needed by both runtimes later, bias toward shared layers.

## Contracts

Reusable boundaries use typed results, DTOs, protocols or named contracts —
not loosely shaped dictionaries and not mixed success/error payloads that force
callers to inspect incidental keys.

Watch for domain models carrying transport or presentation-only fields, and DTOs
introduced where no real reusable boundary exists.

## Transition code

Temporary facades, compatibility paths and fallbacks are acceptable only while
they protect a migration in progress. For each one, be able to answer: what does
it protect, what is the steady state, what must migrate before cleanup.

Remove it once the main callers use the new contract and tests validate the new
path directly. It is overstaying when new code keeps defaulting to it, when it
spans more than one layer, or when nobody can explain why it still exists.

## Validation

- Run the tests covering the changed path directly.
- When shared behavior, startup wiring, runtime flows or external adapters
  change, validate both runtimes — bot startup, command wiring, HTTP routes and
  voice delivery; desktop startup, hotkey wiring, tray and panel flow.
- Name any validation gap explicitly instead of hiding it.

## Environment

Use the repository virtual environment as the default Python runtime for local
development, validation and agent-run commands, not a global Python.

- macOS / Linux / WSL: `.venv/bin/python`
- Windows PowerShell: `.\.venv\Scripts\python.exe`

## Language and encoding

Source files are UTF-8. Repository code, comments, documentation, specs, tests,
commit messages, PR descriptions and AI-generated project artifacts are written
in English by default.

User-facing runtime text may use another language when localization,
language-specific behavior or a locale fixture requires it. Write localized text
directly in UTF-8; do not replace localized characters with Unicode escapes
unless the target format requires it.

## Documentation placement

- `docs/` — durable architecture and operational guides. Update
  `docs/README.md` when navigation changes.
- `openspec/` — change proposals, specs and task lists.
- No implementation-history writeups in `docs/`.
