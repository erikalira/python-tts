# Architecture Diagrams

This guide complements [ARCHITECTURE.md](ARCHITECTURE.md) with smaller, layer-oriented diagrams.

For fully automatic snapshots generated from code, see [ARCHITECTURE_DIAGRAMS_GENERATED.md](ARCHITECTURE_DIAGRAMS_GENERATED.md).

## Why these diagrams exist

The full `pyreverse` output was useful for discovery, but difficult to read as a durable architecture guide. The diagrams in this directory are intentionally curated:

- smaller than the full code graph
- organized by layer or runtime context
- focused on important contracts and coordination paths
- safe to edit manually as the architecture evolves

They are not intended to list every class in the repository.

## Recommended reading order

1. [Layer Overview](diagrams/layer-overview.md)
2. [Shared TTS Core](diagrams/shared-tts-core.md)
3. [Bot Runtime](diagrams/bot-runtime.md)
4. [Desktop Runtime](diagrams/desktop-runtime.md)

## Diagram set

- [diagrams/layer-overview.md](diagrams/layer-overview.md): high-level layer map and dependency direction
- [diagrams/shared-tts-core.md](diagrams/shared-tts-core.md): shared entities, interfaces, and application orchestration
- [diagrams/bot-runtime.md](diagrams/bot-runtime.md): Discord bot composition root, presentation, and infrastructure wiring
- [diagrams/desktop-runtime.md](diagrams/desktop-runtime.md): Desktop App runtime, configuration, UI, tray, and TTS coordination

## How to keep them updated

Use `pyreverse` as a discovery tool, then curate the result into Mermaid instead of publishing the raw output.

Example workflow:

```powershell
pyreverse -o mmd -p tts_hotkey src\application src\core
pyreverse -o mmd -p tts_hotkey src\desktop\app src\desktop\gui src\desktop\services
pyreverse -o mmd -p tts_hotkey src\presentation src\infrastructure src\bot_runtime
```

Recommended maintenance rule:

- regenerate to inspect drift
- update the curated Mermaid `.md` files by hand
- keep each diagram scoped to one architectural conversation

## Editing guidance

- prefer grouping by layer or runtime boundary, not by import graph size
- show stable contracts first, especially interfaces and use cases
- avoid documenting composition-root fields as if they were domain relationships
- when a diagram becomes crowded, split it instead of shrinking everything onto one canvas
