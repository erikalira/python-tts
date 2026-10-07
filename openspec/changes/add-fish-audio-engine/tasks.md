## 1. Configuration and credentials

- [ ] 1.1 Add `fish_audio_api_key` to `src/bot_runtime/settings.py`, read from `FISH_AUDIO` via the existing `_normalized_optional(self._getenv(...))` pattern used by `speak_auth_token`
- [ ] 1.2 Add `fish_audio_model` to the same settings class, read from `FISH_AUDIO_MODEL` with default `s2.1-pro-free`
- [ ] 1.3 Add `"fish-audio"` to the engine allowlist in `Settings.validate()` (`settings.py:144`)
- [ ] 1.4 In `Settings.validate()`, fail with a message naming `FISH_AUDIO` when `tts_config.engine == "fish-audio"` and the key is empty; leave startup unaffected when another engine is selected
- [ ] 1.5 Document `FISH_AUDIO` and `FISH_AUDIO_MODEL` in `.env.example` and `deploy/winsw/.env.windows-server.example`, with the model default and a note that the free model is announced only through 2026-11-30

## 2. Engine implementation

- [ ] 2.1 Add `FishAudioEngine(ITTSEngine)` to `src/infrastructure/tts/engines.py`, taking the API key and model identifier as constructor arguments rather than reading the environment directly
- [ ] 2.2 Implement `generate_audio` with `aiohttp`: POST `https://api.fish.audio/v1/tts`, headers `Authorization: Bearer <key>`, `Content-Type: application/json`, `model: <configured>`; body with `text`, `reference_id` from `config.voice_id`, `format: "mp3"`, and `prosody.speed`
- [ ] 2.3 Add a `_map_rate` static method mapping `rate / 180` clamped to 0.5–2.0, mirroring `EdgeTTSEngine._map_rate`
- [ ] 2.4 Stream the response body to a temp file created with `_create_temp_audio_path(".mp3")` and return `AudioFile(path=...)`
- [ ] 2.5 Map 401, 402, 404, and 422 to distinct exception messages per the spec's error-classification requirement; include the configured model in the 402 message and `voice_id` in the 404 message
- [ ] 2.6 Ensure no code path interpolates the API key into a log record, exception message, or returned string
- [ ] 2.7 Remove the temp file on failure and on `asyncio.CancelledError`, following the cleanup pattern already used by the three existing engines
- [ ] 2.8 Add the `fish-audio` branch to `TTSEngineFactory.create`, passing the key and model through from settings

## 3. Runtime wiring

- [ ] 3.1 Trace how `TTSEngineFactory.create` is reached from `RoutedTTSEngine` and the bot composition root, and supply the key and model without widening the `ITTSEngine` signature or reading the environment inside the factory
- [ ] 3.2 Verify `RoutedTTSEngine`'s per-engine cache (`engines.py:188`) keys correctly for `fish-audio` and does not leak a stale instance when the model changes

## 4. Validation and presentation

- [ ] 4.1 Add `"fish-audio"` to the engine allowlist in `ConfigureTTSUseCase.update_config_async` (`tts_config_use_case.py:54`) and update the rejection message to name all four engines
- [ ] 4.2 Add 32-hexadecimal `reference_id` shape validation, applied only when the resolved engine is `fish-audio`, returning a `ConfigureTTSResult` failure that states the expected format
- [ ] 4.3 Add a `fish-audio` branch to `_build_fallback_voice_label` (`discord_command_handlers.py:37`) so the voice does not fall through to the `R.E.P.O.` pyttsx3 label
- [ ] 4.4 Add a `fish-audio` branch to `_add_voice_resolution_field` (`discord_command_handlers.py:50`) so it does not reach the pyttsx3 branch and call `is_voice_available` against a remote voice ID
- [ ] 4.5 Add the matching i18n entry to `src/presentation/discord_i18n` for the new voice-resolution message, in every locale the catalog already supports
- [ ] 4.6 Confirm by inspection that `voice_catalog.py`, `settings_gui_dialog.py`, and `settings_console_dialog.py` need no edit, and that Fish is therefore absent from the desktop engine picker

## 5. Tests

- [ ] 5.1 Add `test_create_fish_audio_engine` to `tests/unit/infrastructure/test_tts_engines.py`, alongside the three existing factory tests
- [ ] 5.2 Test successful synthesis with a mocked `aiohttp` response: asserts the `model` header, the `reference_id` body field, and that an MP3 `AudioFile` is returned
- [ ] 5.3 Test the rate mapping at 180 → 1.0, 50 → 0.5 (clamped), and 300 → at most 2.0
- [ ] 5.4 Test each of 401, 402, 404, and 422 producing its distinct message, and assert the API key appears in none of them
- [ ] 5.5 Test temp-file cleanup on an HTTP error and on cancellation, mirroring `test_generate_audio_cleans_temp_file_after_cancellation`
- [ ] 5.6 Test that `language` is absent from the request body
- [ ] 5.7 Add settings tests: startup fails when `fish-audio` is selected without `FISH_AUDIO`, succeeds when the key is absent but another engine is selected, and defaults the model to `s2.1-pro-free`
- [ ] 5.8 Add config use-case tests: a malformed `voice_id` is rejected for `fish-audio`, a 32-hex value is accepted, and the same value is left unvalidated for other engines
- [ ] 5.9 Run the full suite and confirm the coverage threshold in `pyproject.toml` still passes

## 6. Deployment and documentation

- [ ] 6.1 Wire `FISH_AUDIO` into `deploy/k8s/base/bot-config.yaml` as a Secret reference, never an inline ConfigMap value, and confirm `.dockerignore` keeps `.env` out of images
- [ ] 6.2 Document the engine in the user-facing docs: how to obtain a `reference_id` from fish.audio, the `/config` example, and that the voice must exist in a reachable Fish account
- [ ] 6.3 Record the measured billing behavior from `design.md` where operators will find it, so the two-ledger model and the 2026-11-30 date are not rediscovered by probing

## 7. Review gates

- [ ] 7.1 Dispatch **Gard** (model: up) for security review: first provider credential in the repository, key handling and non-disclosure, Kubernetes Secret wiring, and the third-party retention of guild members' text
- [ ] 7.2 Resolve open question 1 from `design.md` — whether retention for third-party model training is acceptable, and whether disclosure to guild members is in scope — before merge
- [ ] 7.3 Dispatch **Quinn** (model: down) to verify test coverage against the spec's scenarios, in particular the error-classification and cleanup requirements
