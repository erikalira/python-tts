## Why

The bot's three TTS engines are either robotic (`pyttsx3`) or limited to a fixed
set of vendor voices (`gtts`, `edge-tts`). Fish Audio's `s2.1-pro` family offers
higher-quality multilingual synthesis and a large community voice library, and
its `s2.1-pro-free` model is measured to cost nothing — neither API credit nor
the platform package quota (verified empirically, see design.md).

The free model is announced as available **through 2026-11-30**, so the window
to adopt it at zero cost is short. The integration is also cheap: the engine port
is a single method and the HTTP client (`aiohttp`) is already a dependency.

## What Changes

- Add a `fish-audio` TTS engine to the bot runtime, selectable per guild/user via
  `/config engine:fish-audio`.
- The **user supplies the Fish voice `reference_id` directly** through the
  existing `voice_id` field. No curated Fish voice catalog is shipped: the
  application does not own, track, or validate the existence of voice models.
- Validate the `reference_id` *shape* at config time so a typo fails on `/config`
  with a clear message instead of failing later inside the audio queue.
- Map Fish API error codes (401/402/404/422) to distinct, actionable operator and
  user messages rather than a generic failure.
- Read the API key from a new `FISH_AUDIO` environment variable and the model
  identifier from a new `FISH_AUDIO_MODEL` variable (default `s2.1-pro-free`).
  The model is **never** hardcoded.
- Engine remains **bot-only**. It is not offered in the Desktop App, whose local
  TTS path is a separate stack that supports `pyttsx3` exclusively.

Not breaking: no entity, schema, or existing-engine behavior changes.

## Capabilities

### New Capabilities
- `fish-audio-tts`: Synthesizing speech through the Fish Audio HTTP API, including
  user-supplied voice identity, credential and model configuration, parameter
  mapping from the shared `TTSConfig`, and error classification.

### Modified Capabilities
<!-- None. openspec/specs/ is empty; no existing spec's requirements change. -->

## Impact

**Code (4 files):**
- `src/infrastructure/tts/engines.py` — new `FishAudioEngine`, factory branch.
- `src/application/tts_config_use_case.py` — engine allowlist, `reference_id` validation.
- `src/bot_runtime/settings.py` — engine allowlist, `FISH_AUDIO`, `FISH_AUDIO_MODEL`.
- `src/presentation/discord_command_handlers.py` — voice label and resolution branch.

**Deliberately untouched:**
- `src/core/entities.py` — `TTSConfig` already carries everything needed.
- `deploy/postgres/*.sql` — `engine` is `TEXT NOT NULL` with no CHECK constraint,
  so `"fish-audio"` persists with **no migration**.
- `src/infrastructure/tts/voice_catalog.py` — no Fish entries by design.
- `src/desktop/**` — engine is bot-only.

**Config:** `.env.example`, `deploy/winsw/.env.windows-server.example`,
`deploy/k8s/base/bot-config.yaml` (key as a secret, not a ConfigMap value).

**Dependencies:** none added. Uses `aiohttp>=3.13.5`, already present.

**Security:** introduces the repository's first third-party provider credential
and the first engine that transmits user-authored text to an external service
that retains it for model training. Requires Gard review before merge.
