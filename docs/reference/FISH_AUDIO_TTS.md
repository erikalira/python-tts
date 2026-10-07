# Fish Audio TTS Engine

Reference for the `fish-audio` TTS engine: how to select a voice, how billing
actually behaves, and what each failure mode means.

The engine is **bot-only**. The Desktop App's local synthesis path supports
`pyttsx3` exclusively, so no Fish Audio credential is ever distributed to an
end-user machine. A Desktop App user reaches Fish Audio by speaking through a
bot scope that is configured for it.

## Selecting a voice

Unlike the other engines, this one ships no voice catalog. The voice is a Fish
Audio **`reference_id`** that you supply, and the application neither curates
nor verifies it.

1. Open a voice model on <https://fish.audio> and copy its id from the URL. It is
   32 hexadecimal characters, for example `0123456789abcdef0123456789abcdef`.
2. Paste it into the existing `voice` option:

   ```
   /config voice:0123456789abcdef0123456789abcdef          # for yourself in this guild
   /server-config voice:0123456789abcdef0123456789abcdef   # for the whole guild
   /speak text:olá voice:0123456789abcdef0123456789abcdef  # one utterance only, config unchanged
   ```

The `voice` option takes either a catalog key or a raw Fish `reference_id`. A
catalog key always wins; anything that is not one but has the shape of a
reference_id selects Fish Audio with that voice. Anything else is rejected with
the usual invalid-voice message.

Only the *shape* is validated. A well-formed id that does not exist remotely is
accepted here and fails later with a voice-not-found error. Your stored
`language` is left untouched, because the Fish voice model determines it.

Fish Audio voices do not appear in the voice autocomplete or in the Desktop App
engine picker. That is by design, not an omission — type the id in full and it
is accepted even though it matches no suggestion.

### The voice may not be yours

Public voices on fish.audio are authored by other people. If the author deletes
a voice or makes it private, every scope configured with that id stops speaking.
For anything you depend on, clone the voice into your own Fish Audio account and
configure that id instead.

### Anyone in a guild can choose the voice

`/config voice:` has no permission gate, which is correct for picking a curated
voice for yourself, and means any member can also point your account at any
public voice on fish.audio. `/speak voice:` does the same for a single utterance
without storing anything.

That matters because the fish.audio library contains clones of real people,
including public figures, and impersonation is restricted by both Fish Audio's
and Discord's terms. The account at risk is the one holding `FISH_AUDIO`:
enforcement would take the credential, and the engine with it. On a private
server with known members this is usually acceptable. Before putting this bot
anywhere shared, decide deliberately whether members should hold that lever —
there is currently no switch that disables the un-curated path short of
unsetting `FISH_AUDIO` and losing the engine.

## Configuration

| Variable | Required | Notes |
|---|---|---|
| `FISH_AUDIO` | Only when the engine is used | API key from <https://fish.audio/app/api-keys/>. Store as a secret. In Kubernetes it is an optional key of the `bot-secrets` Secret. |
| `FISH_AUDIO_MODEL` | No | Model sent as the `model` request header. Defaults to `s2.1-pro-free`. Not a secret; lives in the `bot-config` ConfigMap. |

Startup fails when the bot boots with `TTS_ENGINE=fish-audio` and `FISH_AUDIO`
is empty, rather than letting the first `/speak` discover the gap. A guild can
still select the engine through `/config` on a bot that started with a different
default; synthesis then fails with a configuration error until the key is set.

`TTS_LANGUAGE` has no effect on this engine. The Fish voice model determines the
spoken language, so the field is not sent.

`TTS_RATE` maps onto the API's `prosody.speed`: `rate / 180`, clamped to the
accepted 0.5–2.0 range. The 180 default is neutral speed.

## How billing actually behaves

Measured against a live account on 2026-10-07. The vendor blog describes the
free model as "unlimited under Fair Use" and is correct, but the mechanism is
not obvious and is worth recording.

There are **two independent ledgers**, as the API's own 402 response states:
*"API credit is managed independently from platform credit."*

| Ledger | Endpoint | Consumed by |
|---|---|---|
| Platform credit | `GET /wallet/self/package` | The fish.audio web UI |
| API credit | `GET /wallet/self/api-credit` | The paid models (`s1`, `s2.1-pro`) |

The `s2.1-pro-free` model draws on **neither**. A synthesis request with that
model header was measured leaving the platform package balance unchanged, on an
account with zero API credit.

Two consequences:

- **Omitting the `model` header does not silently bill you.** The header
  defaults to the paid `s2.1-pro`, which answers `402` on an account without
  credit — no audio, no charge. The bot therefore always sends the header
  explicitly, and the value is configurable rather than hardcoded.
- **The free model is announced only through 2026-11-30.** When it stops being
  served, the failure is a loud `402` naming the configured model, not a
  surprise invoice. Switch `FISH_AUDIO_MODEL` to `s2.1-pro` with funded API
  credit, or move the affected scopes to another engine.

## Credential status

The key currently on the production host is one that was exposed in a terminal
on 2026-10-07. Rotation was declined at the time, deliberately, and the risk was
accepted on this basis: the account carries `credit: 0.000000`, so the realistic
worst case is consumption of the free quota and misuse of the account's identity
to generate content, not financial loss.

**That bound disappears the moment the account is funded.** Adding API credit —
which this document recommends for the 2026-11-30 free-model sunset — converts an
exposed key from a quota nuisance into a spending credential.

**Rotate the key before adding any API credit.** Treat that as a precondition of
funding, not a follow-up.

There is no local telemetry for misuse of this credential. The observable signal
is the Fish Audio account's own usage and billing history, at fish.audio; that is
where to look if misuse is suspected.

Timeline, for whoever investigates: exposed in a terminal 2026-10-07, rotation
declined the same day, placed on the production host when this engine shipped.

## Failure modes

| Status | Meaning | Action |
|---|---|---|
| `401` | Key invalid, revoked, or malformed | Check `FISH_AUDIO`. |
| `402` | Configured model requires API credit | The free model may have ended. Change `FISH_AUDIO_MODEL` or fund the account. The message names the model in use. |
| `400` *(reference not found)* | The voice no longer exists or is not visible to this account | Reconfigure `voice_id`. The message names the id. |
| `404` | Same as above, per the vendor docs | Reconfigure `voice_id`. |
| `422` | Request rejected as invalid | Read the reason the API reports in the message. |
| timeout | Network failure or a slow provider | Bounded by `TTS_GENERATION_TIMEOUT_SECONDS` (default 60s). |

The documented status for a missing voice is `404`, but an unknown
`reference_id` was measured answering `400 Reference not found`. Both are mapped
to the voice-not-found message; other `400`s keep the generic rejection text.

No failure message contains the API key.

## What this engine does not do

- **No streaming.** The vendor's headline ~90 ms time-to-first-audio is not
  realized: the engine port returns a file path, so the full response is written
  to disk before playback starts. You get the voice quality and the language
  coverage, not the latency.
- **No zero-shot cloning** (`references`), which needs msgpack encoding.
- **No multi-speaker synthesis**, which needs `reference_id` arrays.

## Privacy

Under the free tier's terms, Fish Audio may retain submitted text to improve its
models. In a multi-tenant bot that text is written by guild members, not by the
operator. Weigh this before enabling the engine on a server whose members have
not been told.
