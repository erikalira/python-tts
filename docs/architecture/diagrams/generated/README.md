# Generated Architecture Diagrams

These diagrams are generated automatically with `pyreverse`.

They are intentionally grouped by architectural boundary first, so the generated view stays closer to the repository's Clean Architecture shape.

Automatic diagrams still do not infer Clean Architecture rules on their own. They help inspect structure and drift, while the curated diagrams remain the best explanation of intended boundaries.

## Files

- [core.md](core.md): Automatic class diagram for the innermost shared domain and port contracts in `src.core`.
- [application.md](application.md): Automatic class diagram for reusable use cases and orchestration in `src.application`.
- [presentation-bot.md](presentation-bot.md): Automatic class diagram for delivery entrypoints in `src.presentation` and the Discord bot composition root in `src.bot_runtime`.
- [infrastructure.md](infrastructure.md): Automatic class diagram for adapters and IO-facing implementations in `src.infrastructure`.
- [desktop-runtime.md](desktop-runtime.md): Automatic class diagram for Desktop App runtime, GUI, services, and config modules.

## Regeneration

Run:

```powershell
python scripts/utils/generate_architecture_diagrams.py
```
