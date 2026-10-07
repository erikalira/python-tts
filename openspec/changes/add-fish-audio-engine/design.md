## Context

The bot resolves synthesis through `ITTSEngine` (`src/core/interfaces.py:19`), a
one-method port: `async generate_audio(text, config) -> AudioFile`.
`TTSEngineFactory` (`src/infrastructure/tts/engines.py:199`) maps a config string
to an implementation. Three engines exist today — all of them keyless.

Fish Audio is the first provider in this repository that requires a credential
and the first that transmits user-authored text to a third party which retains
it for model training.

### Measured facts

Probed against a live account on 2026-10-07. These supersede the vendor blog,
which is marketing copy and wrong in at least one material respect.

| Probe | Result |
|---|---|
| `GET /model/ed7de830…` | 200 · `title: Lula` · `languages: ['pt']` · `visibility: public` · `state: trained` · author is a third party |
| `POST /v1/tts` with `model: s2.1-pro-free` | **200** · `audio/mpeg` · 91,532 bytes · valid MP3 (`fffb`) |
| Same request, 21 chars, balance before/after | **delta 0** — the free model consumes no quota |
| `POST /v1/tts` with **no** `model` header | **402** `Insufficient API credit` — no audio, no charge |
| `GET /wallet/self/api-credit` | `credit: 0.000000` · `cumulative_top_up: 0` |
| `GET /wallet/self/package` | `type: free` · `total: 8000` · `balance: 7932` |

Two independent ledgers exist. The 402 response states it directly: *"API credit
is managed independently from platform credit."* The `s2.1-pro-free` model draws
on neither — the 8,000-unit package is consumed by the web UI, and `api-credit`
is consumed by the paid models (`s1`, `s2.1-pro`).

**This corrects an earlier assumption.** An omitted `model` header was expected
to silently bill the paid model. It does not: it fails closed with 402. The
header therefore remains mandatory, but as an *availability* dependency rather
than a financial one — a far more tractable failure mode.

### Constraints

- `TTSConfig` is frozen with five fields (`src/core/entities.py:21`).
- `guild_tts_settings.engine` is `TEXT NOT NULL` with **no CHECK constraint**
  (`deploy/postgres/001_bot_config_schema.sql:3`), so a new engine string needs
  no migration.
- `aiohttp>=3.13.5` is already a dependency.
- The Desktop App does **not** use `ITTSEngine`. It has a parallel stack
  (`TTSEnginePort` in `src/application/desktop_tts.py`, `LocalPyTTSX3Engine` in
  `src/desktop/services/tts_services.py`) whose local path supports `pyttsx3`
  only. A new `ITTSEngine` is unreachable from the desktop by construction.

## Goals / Non-Goals

**Goals:**

- A `fish-audio` engine selectable per guild/user, reaching the Fish Audio API.
- Voice identity supplied entirely by the user; the application owns no catalog.
- Credential and model identifier configurable by environment, never hardcoded.
- Failure modes distinguishable by an operator from the message alone.
- No change to `TTSConfig`, no database migration, no new dependency.

**Non-Goals:**

- **Streaming / time-to-first-audio.** The vendor's headline feature (~90 ms
  TTFA) is unreachable through a port that returns a file path. Capturing it
  requires changing `ITTSEngine` to yield bytes, which touches all four engines,
  `TTSQueueOrchestrator`, and Discord playback. Deliberately deferred; this
  change must not be described as delivering low latency.
- **Fish Audio in the Desktop App.** Would require distributing a credential in a
  PyInstaller executable on end-user machines.
- **A curated Fish voice catalog.** Explicitly rejected (see Decisions).
- **Zero-shot cloning via inline `references`.** Requires msgpack encoding.
- **Multi-speaker synthesis.** Requires `reference_id` arrays and speaker tags.

## Decisions

### User-supplied `reference_id` instead of a curated catalog

Fish voice identifiers are account-scoped and community-authored, unlike
`edge-tts` where `pt-BR-FranciscaNeural` is a stable vendor ID. Shipping a
curated list would mean the application owns assets it does not control: when an
author deletes a public voice, the shipped catalog silently points at a 404.

The user pastes the `reference_id` into the existing `voice_id` field.

*Alternative considered:* fetch voices from `GET /model` at startup and populate
the catalog dynamically. Rejected — it adds a startup network dependency and a
cache invalidation problem to solve a need no one has expressed.

**Consequence that shrinks the change:** `_list_engine_values()`
(`settings_gui_dialog.py:357`) derives the desktop engine list from catalog
membership intersected with a hardcoded order. With no Fish catalog entries and
no edit to that list, Fish never appears in the desktop UI. Combined with the
separate desktop TTS stack, bot-only scope requires **zero desktop edits**. The
blast radius drops from seven hardcoded sites to four.

### Validate identifier shape, not existence

A 32-hex check at `/config` time converts the most common user error (a typo or a
pasted URL) from an async failure inside the audio queue into an immediate,
legible command error. Existence is deliberately *not* checked: that would add a
network round trip to `/config` and still race against later deletion.

### `rate` maps to `prosody.speed`

`rate` is 50–300 with a 180 baseline; `prosody.speed` is 0.5–2.0 with a 1.0
baseline. So `speed = rate / 180`, clamped. This mirrors the existing precedent
in `EdgeTTSEngine._map_rate` (`engines.py:175`), which maps the same field to a
percentage. `language` is not sent — the Fish voice model determines it, so
sending it would imply control the API does not offer.

*Alternative considered:* extend `TTSConfig` with Fish-specific fields
(`temperature`, `latency`, `format`). Rejected — it would unfreeze a value object
shared by every layer and force a migration, to expose knobs that are
deployment-wide rather than per-guild. Those belong in environment variables.

### Fail closed at startup when the engine is selected without a key

Validating in `Settings.validate()` turns a missing credential into a refused
boot rather than a runtime failure discovered by the first user to type `/speak`.
The check is conditional on the engine actually being selected, so an operator
who never uses Fish is unaffected.

## Risks / Trade-offs

**User text is retained for third-party model training** → The free tier permits
retention for model improvement. In a multi-tenant Discord bot this is not the
operator's own text but that of any member of any guild. No mitigation exists at
the code level; this is a disclosure and scope decision, and the reason Gard must
review before merge. **Unresolved — see Open Questions.**

**The free model is announced only through 2026-11-30 (54 days out)** → Because
the failure mode is a loud 402 and not silent billing, the mitigation is cheap:
`FISH_AUDIO_MODEL` is configurable, the 402 message names the configured model,
and an operator switches to `s2.1-pro` with credit, or to another engine. No
automatic fallback is implemented — a silent downgrade to a different voice would
be more confusing than an explicit failure.

**A configured voice can disappear at any time** → Public community voices are
third-party assets. The 404 path yields a message naming `voice_id` and telling
the user to reconfigure. Operators who depend on a specific voice in production
should clone it into their own Fish account and use that identifier.

**Cloned public-figure voices** → The voice probed during exploration
(`ed7de830…`, "Lula") is a clone of a public figure authored by a third party.
Both Fish Audio's and Discord's terms restrict impersonation, and the account at
risk is the one holding the key in `FISH_AUDIO`. Out of scope for this change,
but operators should know the exposure is account-level.

**First provider credential in the repository** → No prior art for provider
secrets exists here (only `DISCORD_TOKEN` and `BOT_SPEAK_TOKEN`). The key must
reach Kubernetes as a Secret, not a ConfigMap value, and must be excluded from
every log and user-facing path.

**Network latency inside the audio queue** → Synthesis becomes a remote call that
can be slow or hang. Already bounded by `TTS_GENERATION_TIMEOUT_SECONDS`
(default 60s, `src/core/timeouts.py`), which the queue orchestrator honors. No
new mechanism needed.

## Migration Plan

No schema migration — `engine` is unconstrained `TEXT`.

1. Provision `FISH_AUDIO` as a secret in each target environment. Leave
   `FISH_AUDIO_MODEL` unset to accept the `s2.1-pro-free` default.
2. Deploy. No scope uses `fish-audio` yet, so behavior is unchanged and startup
   validation stays inert.
3. Opt a single scope in with `/config voice:<reference_id>` (or
   `/server-config voice:<reference_id>` for a whole guild) and verify
   playback. Example placeholder: `0123456789abcdef0123456789abcdef`.

**Rollback:** set the affected scopes back to a prior engine via `/config`, or
revert the deployment. Nothing persisted by this change is unreadable by the
previous version — an unknown `engine` string is rejected by validation and the
scope falls back to configuring a known engine.

## Findings from implementation and review

Recorded here because each one contradicts something this document or the spec
originally asserted.

**A missing voice answers 400, not 404.** The vendor documents 404 for a voice
that does not exist. An unknown `reference_id` was measured answering
`400 Reference not found` (2026-10-07). Both now map to the voice-not-found
message; other 400s keep the generic rejection text.

**The credential was printed to a terminal during implementation.** Three
settings tests asserted on the *absence* of `FISH_AUDIO` — a shape no prior test
in that file had — and `Config` falls back to `os.environ`, so they read the
developer's real key and pytest printed it in a failing comparison diff. Fixed
structurally: `tests/conftest.py` now sanitizes provider credentials for the
whole suite via an autouse fixture, so a future provider inherits the guarantee
instead of having to remember a fixture. **Any key that reached a terminal
scrollback, a multiplexer history, or a CI log must be treated as exposed and
rotated.** This document previously said nothing about rotation.

**Rotation was declined (2026-10-07) and the key was placed on the production
host anyway.** The risk is bounded only while the account has no API credit: the
worst case today is free-quota consumption and misuse of the account's identity,
not spending. Funding the account for the 2026-11-30 sunset removes that bound,
so **rotating before adding credit is a precondition of funding**, recorded in
`docs/reference/FISH_AUDIO_TTS.md` where an operator will meet it.

**There was no per-guild opt-in, and the spec described a command that did not
exist.** This document and the spec originally said to pilot one guild with
`/config engine:fish-audio voice_id:<id>`. `/config` and `/server-config` take a
single `voice` parameter resolved through a catalog lookup, and Fish Audio
deliberately has no catalog entries, so the engine was reachable only through
`TTS_ENGINE` (deployment wide, every guild at once) and the HTTP `/speak`
override. **Resolved** by making `voice` accept a raw reference_id as a
fall-through: a catalog key still wins, and a 32-hex value that matches no key
selects `fish-audio`. This adds no command and no parameter, keeps the voice
user-supplied, and restores a per-scope opt-in so the migration plan's pilot
step is executable. The same fall-through applies to `/speak voice:` for a
single utterance.

**The HTTP `/speak` override accepted an unvalidated engine and voice.**
`_parse_config_override` took both straight from the request body. The mechanism
predates this change, but before it every engine was keyless, so an unvalidated
engine override cost nothing; a caller holding `BOT_SPEAK_TOKEN` — which is
distributed to Desktop App clients — could otherwise drive the operator's
credentialed account with an arbitrary voice. Now validated against
`SUPPORTED_TTS_ENGINES` and the `reference_id` shape, returning 400.

**The repository shipped a public-figure impersonation clone as its canonical
example**, including inside the user-facing `/config` validation error. Replaced
everywhere with the non-resolving placeholder
`0123456789abcdef0123456789abcdef`. The real id is retained only in this
document, as the record of the exposure rather than a recommendation.

**`FishAudioSettings` disclosed the key through `repr`.** Frozen protects
integrity, not confidentiality; the auto-generated repr would print the
credential in any debug log or assertion diff. `api_key` is now `repr=False`.

**Two durable sinks relay the provider's error body.** A failed item's
`error_message` is serialized into Redis (retained `REDIS_COMPLETED_ITEM_TTL_SECONDS`,
900s default) and recorded on an OTel span exported to the OTLP endpoint. The
Discord and HTTP presenters do *not* render it, so no user-facing disclosure
path exists today — but the relayed body is content from outside the trust
boundary, so it is now truncated **and** scrubbed of the credential before being
used in a message.

## Open Questions

1. ~~**Is third-party retention of guild members' text acceptable?**~~
   **Decided 2026-10-07:** accepted for this deployment, which is a private
   server where it is not a concern. No formal member notice is planned. The
   containment that remains in code is a startup WARN naming the retention and a
   clause in the `/config` voice-resolution embed, in both locales. This
   decision is scoped to the current deployment: a public or shared server would
   reopen it, and Gard's judgment was that such a server needs member disclosure
   before `FISH_AUDIO` is set.
2. **Should the 402 path alert an operator** (log level, metric, Prometheus rule)
   rather than only surfacing to the user who typed `/speak`? Relevant from
   2026-12-01, when the free model may stop answering. `deploy/observability/`
   already holds alert rules.
