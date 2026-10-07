## ADDED Requirements

### Requirement: Fish Audio engine selection

The bot SHALL accept `fish-audio` as a valid TTS engine identifier wherever
`gtts`, `pyttsx3`, and `edge-tts` are accepted, and SHALL route synthesis for
that identifier to the Fish Audio HTTP API.

#### Scenario: Operator selects the engine at runtime
- **WHEN** a user runs `/config engine:fish-audio` in a guild
- **THEN** the configuration SHALL be accepted and persisted for that scope
- **AND** subsequent `/speak` requests in that scope SHALL synthesize via Fish Audio

#### Scenario: Engine selected through environment
- **WHEN** the bot starts with `TTS_ENGINE=fish-audio`
- **THEN** startup validation SHALL accept the value as a known engine

#### Scenario: Unknown engine still rejected
- **WHEN** a user runs `/config engine:fish-audioo`
- **THEN** the command SHALL fail with a message naming every valid engine
- **AND** the stored configuration SHALL remain unchanged

### Requirement: User-supplied voice identity

The application SHALL treat the Fish Audio voice as data owned by the user, not
by the application. The `voice_id` field of the TTS configuration SHALL carry the
Fish `reference_id` verbatim and be sent unmodified as the request's
`reference_id`. The application SHALL NOT ship, curate, or maintain a catalog of
Fish Audio voices, and SHALL NOT verify that a given voice model exists before a
synthesis attempt.

#### Scenario: User configures an arbitrary voice model
- **WHEN** a user runs `/config engine:fish-audio voice_id:ed7de8309b7f4643932df8f4b56ac988`
- **THEN** the value SHALL be persisted verbatim as `voice_id`
- **AND** synthesis requests SHALL send it as the `reference_id` field

#### Scenario: Voice autocomplete excludes Fish Audio
- **WHEN** a user browses the `/config` voice autocomplete options
- **THEN** no Fish Audio voices SHALL be listed
- **AND** the autocomplete SHALL continue to list `gtts`, `edge-tts`, and `pyttsx3` voices

### Requirement: Voice identifier shape validation

The system SHALL reject a syntactically impossible Fish `reference_id` at
configuration time rather than at synthesis time. A valid identifier SHALL be
exactly 32 hexadecimal characters. Validation SHALL be limited to shape: a
well-formed identifier that does not exist remotely SHALL be accepted at
configuration time and surface later as a synthesis error.

#### Scenario: Malformed identifier rejected at config time
- **WHEN** a user runs `/config engine:fish-audio voice_id:not-a-valid-id`
- **THEN** the command SHALL fail with a message stating the expected format
- **AND** no synthesis request SHALL be sent to Fish Audio
- **AND** the stored configuration SHALL remain unchanged

#### Scenario: Well-formed but nonexistent identifier accepted at config time
- **WHEN** a user configures a 32-hexadecimal identifier that no longer exists remotely
- **THEN** the `/config` command SHALL succeed
- **AND** the next synthesis attempt SHALL fail with the voice-not-found message

### Requirement: Credential and model configuration

The API key SHALL be read from the `FISH_AUDIO` environment variable and SHALL
NOT appear in logs, error messages, Discord responses, or persisted
configuration. The model identifier SHALL be read from `FISH_AUDIO_MODEL`,
defaulting to `s2.1-pro-free`, and SHALL always be sent as the `model` request
header. The model identifier SHALL NOT be hardcoded at any call site.

#### Scenario: Engine selected without a configured key
- **WHEN** the bot starts with `TTS_ENGINE=fish-audio` and `FISH_AUDIO` unset or empty
- **THEN** startup validation SHALL fail with a message naming the missing variable
- **AND** the bot SHALL NOT start

#### Scenario: Key absent but engine unused
- **WHEN** the bot starts with `FISH_AUDIO` unset and no scope configured for `fish-audio`
- **THEN** startup SHALL succeed
- **AND** the other engines SHALL remain fully usable

#### Scenario: Model header always present
- **WHEN** the engine issues any synthesis request
- **THEN** the request SHALL carry a `model` header holding the configured value
- **AND** the value SHALL default to `s2.1-pro-free` when `FISH_AUDIO_MODEL` is unset

#### Scenario: Credential never disclosed
- **WHEN** any Fish Audio request fails for any reason
- **THEN** the logged and user-facing messages SHALL NOT contain the API key

### Requirement: Configuration parameter mapping

The engine SHALL translate the shared `TTSConfig` into Fish Audio request
parameters without extending the `TTSConfig` entity. The `rate` field SHALL map
to `prosody.speed` as `rate / 180`, clamped to the API's accepted range of 0.5
through 2.0. Because the Fish voice model determines the spoken language, the
`language` field SHALL NOT be sent.

#### Scenario: Default rate maps to neutral speed
- **WHEN** synthesis runs with a `rate` of 180
- **THEN** the request SHALL specify a `prosody.speed` of 1.0

#### Scenario: Low rate clamped to the accepted minimum
- **WHEN** synthesis runs with a `rate` of 50
- **THEN** the request SHALL specify a `prosody.speed` of 0.5

#### Scenario: High rate stays within the accepted maximum
- **WHEN** synthesis runs with a `rate` of 300
- **THEN** the request SHALL specify a `prosody.speed` no greater than 2.0

#### Scenario: Audio returned in a playable format
- **WHEN** synthesis succeeds
- **THEN** the engine SHALL return an `AudioFile` pointing at an MP3 file on disk

### Requirement: Error classification

The engine SHALL distinguish Fish Audio failure modes and surface an actionable
message for each, rather than a generic synthesis failure.

#### Scenario: Invalid or revoked credential
- **WHEN** Fish Audio responds with status 401
- **THEN** the failure message SHALL indicate an invalid or missing API key

#### Scenario: Free model withdrawn or quota exhausted
- **WHEN** Fish Audio responds with status 402
- **THEN** the failure message SHALL indicate that the configured model requires API credit
- **AND** the message SHALL name the configured model identifier

#### Scenario: Voice model unavailable
- **WHEN** Fish Audio responds with status 404
- **THEN** the failure message SHALL indicate that the configured voice no longer exists
- **AND** the message SHALL instruct the user to reconfigure `voice_id`

#### Scenario: Request rejected as invalid
- **WHEN** Fish Audio responds with status 422
- **THEN** the failure message SHALL indicate a rejected request and include the reason reported by the API

#### Scenario: Network failure or timeout
- **WHEN** the request times out or the connection fails
- **THEN** the engine SHALL raise a synthesis failure
- **AND** the existing TTS generation timeout SHALL bound the attempt

### Requirement: Temporary audio lifecycle

The engine SHALL NOT leak temporary audio files, matching the cleanup guarantees
of the existing engines.

#### Scenario: Failed synthesis removes its artifact
- **WHEN** a synthesis attempt fails after a temporary file was created
- **THEN** that temporary file SHALL be removed before the error propagates

#### Scenario: Cancelled synthesis removes its artifact
- **WHEN** a synthesis attempt is cancelled mid-request
- **THEN** the temporary file SHALL be removed
- **AND** the cancellation SHALL propagate to the caller

### Requirement: Engine scope limited to the bot runtime

Fish Audio SHALL be available only in the bot runtime. The Desktop App SHALL NOT
offer it for local synthesis, and the API key SHALL NOT be distributed to
end-user machines.

#### Scenario: Desktop engine picker omits Fish Audio
- **WHEN** a user opens the Desktop App settings dialog
- **THEN** the engine options SHALL be limited to `gtts`, `pyttsx3`, and `edge-tts`

#### Scenario: Desktop reaches Fish Audio only through the bot
- **WHEN** a Desktop App user triggers speech for a scope configured to `fish-audio`
- **THEN** synthesis SHALL occur in the bot runtime
- **AND** the Desktop App SHALL NOT require a Fish Audio credential
