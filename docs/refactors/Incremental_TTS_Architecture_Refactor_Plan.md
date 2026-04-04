# Incremental TTS Architecture Refactor Plan

## Goal

Reduce the main architectural risks in the shared TTS flow without breaking the two supported execution modes:

- Discord bot
- Windows hotkey desktop app

This plan is intentionally incremental. Each step should be reversible, behavior-preserving where possible, and validated before the next step begins.

## Why This Refactor Exists

The current architecture is in a solid intermediate state, but two risks deserve priority:

1. infrastructure concerns leaking into `src/core/`
2. too much orchestration concentrated in `SpeakTextUseCase`

The aim is not a rewrite. The aim is to make the codebase easier to evolve safely.

## Scope

Primary focus:

- `src/application/use_cases.py`
- `src/core/entities.py`
- `src/presentation/discord_commands.py`
- `src/presentation/http_controllers.py`
- `src/infrastructure/audio_queue.py`

Secondary impact:

- bot composition and startup flow
- desktop runtime integrations that reuse shared TTS logic
- unit tests around application and presentation layers

## Refactor Strategy

Apply the project playbook:

1. extract first
2. replace second
3. remove old code last
4. validate both app modes after each meaningful step

This work should be treated as primarily structural, with moderate runtime risk in async queue and voice playback flows.

## Step 1: Introduce Typed Result Objects

### Objective

Replace ad-hoc `dict` contracts in shared TTS flows with typed result objects while preserving current external behavior.

### Main changes

- add typed result models for `speak`, `join`, `leave`, and `voice_context`
- keep temporary compatibility helpers such as `to_dict()` or equivalent adapters
- migrate callers gradually instead of changing every presentation layer at once

### Likely files

- `src/application/use_cases.py`
- `src/application/results.py` or similar new module
- `src/presentation/discord_commands.py`
- `src/presentation/http_controllers.py`

### Why this step comes first

It stabilizes the application contract before the internal logic is split into smaller pieces.

### Validation

- run `tests/unit/application/test_use_cases.py`
- run `tests/unit/presentation/test_discord_commands.py`
- run `tests/unit/presentation/test_http_controllers.py`
- validate `/join`, `/leave`, and `/speak`
- validate HTTP `/speak`

## Step 2: Extract Voice Channel Resolution and Security Validation

### Objective

Move channel-discovery and channel-safety rules out of `SpeakTextUseCase` into a dedicated application component.

### Main changes

- extract guild inference
- extract member presence checks
- extract cross-guild validation
- extract channel resolution logic now implemented in private methods such as `_find_voice_channel` and `_is_user_in_channel`

### Likely files

- `src/application/use_cases.py`
- `src/application/voice_channel_resolution.py` or similar new module

### Why this step is safe

This is mostly a mechanical extraction of logic that already exists, with low presentation impact.

### Validation

- run `tests/unit/application/test_use_cases.py`
- add or update tests for:
  - user not in voice channel
  - detected channel in another guild
  - bot connected to a different channel
  - auto-join behavior to the member's current channel

## Step 3: Extract Queue and Playback Orchestration

### Objective

Reduce the size and responsibility of `SpeakTextUseCase` by moving queue-drain and playback orchestration into a dedicated collaborator.

### Main changes

- move queue processing helpers out of `SpeakTextUseCase`
- isolate background task lifecycle per guild
- isolate playback execution flow from request validation flow
- keep `SpeakTextUseCase` focused on request intake and orchestration

### Likely files

- `src/application/use_cases.py`
- `src/application/tts_queue_orchestrator.py` or similar new module
- `src/infrastructure/audio_queue.py`

### Risk note

This is the highest-risk step because it touches async flow, queue ordering, and playback lifecycle.

### Validation

- run `tests/unit/application/test_use_cases.py`
- add or update queue-focused tests
- validate multiple requests in the same guild
- validate isolation between guild queues
- validate voice playback still completes and advances the queue

## Step 4: Remove Filesystem Cleanup from `src/core/`

### Objective

Make the core layer pure again by removing file deletion behavior from domain entities.

### Main changes

- turn `AudioFile` into a pure data structure
- move cleanup responsibility into infrastructure or an injected cleanup port
- update playback flow to call cleanup through a boundary-respecting collaborator

### Likely files

- `src/core/entities.py`
- `src/core/interfaces.py`
- `src/application/use_cases.py`
- `src/infrastructure/tts/` new cleanup helper if needed

### Why this step comes later

It is easier and safer once the execution flow has already been split into smaller units.

### Validation

- run `tests/unit/core/test_entities.py`
- run `tests/unit/application/test_use_cases.py`
- run `tests/integration/infrastructure/test_engines_integration.py`
- confirm temporary audio cleanup still happens correctly

## Step 5: Consolidate Presentation Mappers

### Objective

Remove repeated message/status translation logic from Discord and HTTP entrypoints.

### Main changes

- move result-to-message mapping into dedicated presenters or mappers
- keep controllers and command handlers focused on transport and UI interaction
- reduce duplication between Discord and HTTP response translation

### Likely files

- `src/presentation/discord_commands.py`
- `src/presentation/http_controllers.py`
- `src/presentation/discord_presenters.py` or similar new module
- `src/presentation/http_presenters.py` or similar new module

### Validation

- run `tests/unit/presentation/test_discord_commands.py`
- run `tests/unit/presentation/test_http_controllers.py`
- manually verify user-facing responses still match expected behavior

## Recommended Execution Order

1. typed result objects
2. voice channel and security extraction
3. queue and playback extraction
4. filesystem cleanup removal from core
5. presentation mapper consolidation

## Validation Checklist For Every Step

- run relevant unit tests
- verify imports and dependency direction still make sense
- validate Discord bot startup through `src/bot.py`
- validate Windows desktop app startup through `app.py`
- manually test the changed runtime path
- remove old code only after the replacement path is stable

## Expected Outcome

After this refactor sequence, the repository should be easier to scale in three important ways:

- shared application contracts become more explicit and safer to evolve
- the bot TTS flow becomes easier to modify without destabilizing unrelated concerns
- the core layer becomes cleaner and less coupled to infrastructure behavior

## Notes

- This plan favors small PRs over a single large refactor branch.
- If a step forces behavior changes, document that explicitly before continuing.
- If documentation or navigation changes again, update `docs/README.md`.
