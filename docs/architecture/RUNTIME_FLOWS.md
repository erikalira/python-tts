# Runtime Flows

This guide helps contributors quickly understand how the two application modes start, compose dependencies, and reach the main shared flows.

## Why this exists

The repository has two independent runtimes:

- Discord bot
- Windows Desktop App

The architecture is easier to maintain when contributors can identify:

- the entrypoint for each runtime
- the composition root
- the main runtime coordinator
- where shared logic begins

For visual structure, pair this guide with [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md).

## Discord bot flow

### Entry path

1. `src/bot.py`
2. `src/bot_runtime/container.py`
3. `src/presentation/discord_commands.py`
4. shared use cases in `src/application/`

### Main responsibilities

- `src/bot.py`
  Starts the bot process and runtime setup.

- `src/bot_runtime/container.py`
  Builds dependencies and wires the Discord client, HTTP server, presenters, and use cases.

- `src/presentation/discord_commands.py`
  Registers slash commands and delegates command flows.

- `src/presentation/http_controllers.py`
  Handles HTTP requests exposed by the bot runtime.

### Shared logic boundary

Once the request reaches a use case in `src/application/`, the flow should be reusable and not Discord-specific.

## Desktop App flow

### Entry path

1. `app.py`
2. `src/desktop/app/bootstrap.py`
3. `src/desktop/app/desktop_app.py`
4. Desktop runtime coordinators and services
5. shared use cases in `src/application/` where applicable

### Main responsibilities

- `app.py`
  Starts the Desktop App runtime.

- `src/desktop/app/bootstrap.py`
  Creates the Desktop App composition root.

- `src/desktop/app/desktop_app.py`
  Coordinates initialization, runtime lifecycle, UI, tray, hotkeys, and shutdown.

- `src/desktop/app/tts_runtime.py`
  Coordinates TTS execution feedback and keyboard cleanup.

- `src/desktop/gui/main_window.py`
  Hosts the main panel used for configuration, visibility, and operator feedback.

## Shared flow examples

### Bot `/speak`

1. Discord slash command enters through `DiscordCommands`
2. A `TTSRequest` is built
3. `SpeakTextUseCase` in `src/application/` processes and queues the request
4. Presentation maps the typed result back to Discord

### Desktop hotkey to speech

1. Hotkey capture happens in `src/desktop/services/`
2. `DesktopAppHotkeyHandler` forwards captured text
3. `SpeakTextExecutionUseCase` coordinates execution
4. `DesktopAppTTSService` routes to remote bot delivery or local fallback
5. Desktop notification and cleanup are handled in desktop runtime modules

## Reading order for new contributors

When onboarding into the codebase, prefer this reading order:

1. `README.md`
2. `docs/architecture/ARCHITECTURE.md`
3. this file
4. the entrypoint and composition root for the runtime you are touching
5. the relevant shared use case or desktop runtime coordinator

## Design note

Large files are acceptable when they act as:

- entrypoints
- composition roots
- runtime coordinators
- narrow facades used during safe refactors

They should still remain readable enough for a contributor to follow the flow without relying on hidden historical knowledge.
