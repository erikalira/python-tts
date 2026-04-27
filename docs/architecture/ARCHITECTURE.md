# Project Architecture - Windows Desktop App And Discord Bot

## Overview

This project contains two independent applications:

1. A Discord bot with an HTTP endpoint for TTS
2. A Windows Desktop App with hotkeys, GUI, and system tray integration

Both follow Clean Architecture and SOLID principles to preserve:

- low coupling between layers
- high cohesion inside modules
- reuse of shared rules in `src/application/` and `src/core/`
- independence between the bot and the Desktop App

## Diagrams

For a visual architecture reading path, use the curated diagrams instead of the raw `pyreverse` output:

- [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)
- [diagrams/layer-overview.md](diagrams/layer-overview.md)
- [diagrams/shared-tts-core.md](diagrams/shared-tts-core.md)
- [diagrams/bot-runtime.md](diagrams/bot-runtime.md)
- [diagrams/desktop-runtime.md](diagrams/desktop-runtime.md)

These diagrams are organized by layer and runtime context so they remain readable as durable documentation.

## Entry Points

### Desktop App

- official entrypoint: `app.py`
- internal runtime: `src/desktop/`
- composition root: `src/desktop/app/bootstrap.py`
- main runtime coordinator: `src/desktop/app/desktop_app.py`

### Discord Bot

- official entrypoint: `src/bot.py`
- HTTP server: `src/infrastructure/http/server.py`
- local HTTP bind defaults to `127.0.0.1`; to expose it externally during deployment, set `DISCORD_BOT_HOST=0.0.0.0`

## Main Structure

```text
src/
  core/                  # entities, value objects, and pure interfaces
  application/           # shared use cases and orchestration
  infrastructure/        # external integrations and IO
  presentation/          # controllers and input flows
  desktop/               # internal Desktop App runtime
    adapters/            # keyboard, tray, and local TTS adapters
    app/                 # bootstrap and main Desktop App runtime
    config/              # DesktopAppConfig, repository, validation, environment
    gui/                 # Desktop App interfaces and windows
    services/            # Desktop App hotkeys, notifications, and engines
```

## Desktop App

### Config

The Desktop App uses `DesktopAppConfig` as its main configuration container.

```python
@dataclass
class DesktopAppConfig:
    tts: TTSConfig
    discord: DiscordConfig
    hotkey: HotkeyConfig
    interface: InterfaceConfig
    network: NetworkConfig
```

Main files:

- `src/desktop/config/desktop_config.py`
- `src/desktop/config/models.py`
- `src/desktop/config/repository.py`
- `src/desktop/config/validation.py`

The local environment is loaded from `.env`, which provides Desktop App defaults and helps reproduce local and test scenarios.

### Runtime

The main Desktop App runtime lives in `src/desktop/app/desktop_app.py`.

Main responsibilities:

- load configuration
- assemble TTS, hotkeys, and tray integration
- open the main panel when Tkinter is available
- coordinate reconfiguration without mixing business rules into GUI code

### TTS And Hotkeys

The Desktop App is split into smaller responsibilities:

- `src/desktop/app/tts_runtime.py`: threading, cleanup, and execution feedback
- `src/desktop/services/tts_services.py`: TTS engines and delivery selection
- `src/desktop/services/hotkey_services.py`: hotkey monitoring and management
- `src/desktop/services/hotkey_capture.py`: pure text-capture state

## Dependency Rules

- `src/core/` does not depend on external layers
- `src/application/` depends only on `src/core/`
- `src/infrastructure/` may depend on `application` and `core`
- `src/presentation/` delegates to `application`
- `src/desktop/` should contain only Desktop App-specific runtime, adapters, and coordination
- logic shared by the bot and Desktop App should be extracted to `src/application/` or `src/core/`

## Execution

```bash
# Bot
python -m src.bot

# Desktop App
python app.py
```

## Tests

Desktop App tests live in `tests/unit/desktop/`.

Notes:

- Desktop App tests are standardized under `tests/unit/desktop/`
- public symbols use the `Desktop App` naming convention
- the local test environment uses `.env` as the basis for some defaults and scenarios

## References

- [../desktop/DESKTOP_APP_GUIDE.md](../desktop/DESKTOP_APP_GUIDE.md)
