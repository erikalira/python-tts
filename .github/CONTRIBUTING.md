# Contributing To TTS Hotkey Windows

Thank you for your interest in contributing. This project follows Clean
Architecture and SOLID principles.

## Project Architecture

The project is organized in layers:

```text
src/
|-- core/                 # Domain layer: pure entities and interfaces
|   |-- entities.py       # pure business entities
|   `-- interfaces.py     # contracts and abstractions
|
|-- application/          # Application layer: use cases and orchestration
|
|-- infrastructure/       # Infrastructure layer: external integrations and IO
|   |-- tts/              # TTS implementations
|   |-- discord/          # Discord implementations
|   `-- http/             # HTTP server
|
`-- presentation/         # Presentation layer: controllers and Discord commands
    |-- http_controllers.py
    `-- discord_commands.py
```

### Dependency Rules

Dependencies should point inward:

```text
Presentation -> Application -> Domain <- Infrastructure
```

- Presentation may depend on Application and Domain
- Application may depend on Domain
- Infrastructure implements Domain/Application-facing contracts
- Domain must remain pure Python and must not depend on outer layers
- Application must not import Infrastructure directly

The canonical repository rules live in `.specify/`. If this file and `.specify/`
conflict, `.specify/` wins.

## Pull Request Checklist

Before opening a PR, check:

- [ ] The change is in the correct layer
- [ ] Dependencies still point inward
- [ ] No circular imports were introduced
- [ ] Shared behavior was not duplicated between bot and Desktop App runtimes
- [ ] New contracts are explicit and typed where useful
- [ ] Unit tests cover new or changed behavior
- [ ] Coverage is maintained or improved
- [ ] `pytest` passes locally for the changed path
- [ ] `ruff check .` passes
- [ ] Durable docs were updated when architecture, setup, deployment, or runtime behavior changed

## Adding Features

Prefer the smallest architecture-safe change that solves the problem.

For example, when adding a new TTS engine:

1. Keep the reusable contract in the inner layers if one is needed.
2. Implement provider-specific behavior in Infrastructure.
3. Wire the concrete adapter in a composition root or runtime layer.
4. Add focused tests around the new behavior and integration point.

```python
class ITTSEngine(ABC):
    @abstractmethod
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        pass
```

```python
class ElevenLabsEngine(ITTSEngine):
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        pass
```

## What Not To Do

Do not import Infrastructure into Application use cases:

```python
from src.infrastructure.tts.engines import GTTSEngine

class SpeakTextUseCase:
    def __init__(self):
        self._engine = GTTSEngine()
```

Do not place business logic in Presentation controllers:

```python
class SpeakController:
    async def speak(self, request):
        # Business rules do not belong here.
        pass
```

Do not couple Domain entities to external libraries:

```python
import discord

@dataclass
class TTSRequest:
    text: str
    discord_client: discord.Client
```

## Resources

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://www.digitalocean.com/community/conceptual_articles/s-o-l-i-d-the-first-five-principles-of-object-oriented-design)
- [Dependency Injector Documentation](https://python-dependency-injector.ets-labs.org/)

## Reporting Bugs

When reporting a bug:

1. Check whether it has already been reported.
2. Include reproduction steps.
3. Include relevant logs.
4. Mention Python version and operating system.

## Questions

Open an issue with the `question` label.
