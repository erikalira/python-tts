## 1. Configuration and credentials

- [x] 1.1 Add `fish_audio_api_key` to `src/bot_runtime/settings.py`, read from `FISH_AUDIO` via the existing `_normalized_optional(self._getenv(...))` pattern used by `speak_auth_token`
- [x] 1.2 Add `fish_audio_model` to the same settings class, read from `FISH_AUDIO_MODEL` with default `s2.1-pro-free`
- [x] 1.3 Add `"fish-audio"` to the engine allowlist in `Settings.validate()` (`settings.py:144`)
- [x] 1.4 In `Settings.validate()`, fail with a message naming `FISH_AUDIO` when `tts_config.engine == "fish-audio"` and the key is empty; leave startup unaffected when another engine is selected
- [x] 1.5 Document `FISH_AUDIO` and `FISH_AUDIO_MODEL` in `.env.example` and `deploy/winsw/.env.windows-server.example`, with the model default and a note that the free model is announced only through 2026-11-30

## 2. Engine implementation

- [x] 2.1 Add `FishAudioEngine(ITTSEngine)` to `src/infrastructure/tts/engines.py`, taking the API key and model identifier as constructor arguments rather than reading the environment directly
- [x] 2.2 Implement `generate_audio` with `aiohttp`: POST `https://api.fish.audio/v1/tts`, headers `Authorization: Bearer <key>`, `Content-Type: application/json`, `model: <configured>`; body with `text`, `reference_id` from `config.voice_id`, `format: "mp3"`, and `prosody.speed`
- [x] 2.3 Add a `_map_rate` static method mapping `rate / 180` clamped to 0.5–2.0, mirroring `EdgeTTSEngine._map_rate`
- [x] 2.4 Stream the response body to a temp file created with `_create_temp_audio_path(".mp3")` and return `AudioFile(path=...)`
- [x] 2.5 Map 401, 402, 404, and 422 to distinct exception messages (amended during implementation: a missing voice was measured answering **400 `Reference not found`**, not 404, so both map to the voice-not-found message) per the spec's error-classification requirement; include the configured model in the 402 message and `voice_id` in the 404 message
- [x] 2.6 Ensure no code path interpolates the API key into a log record, exception message, or returned string
- [x] 2.7 Remove the temp file on failure and on `asyncio.CancelledError`, following the cleanup pattern already used by the three existing engines
- [x] 2.8 Add the `fish-audio` branch to `TTSEngineFactory.create`, passing the key and model through from settings

## 3. Runtime wiring

- [x] 3.1 Trace how `TTSEngineFactory.create` is reached from `RoutedTTSEngine` and the bot composition root, and supply the key and model without widening the `ITTSEngine` signature or reading the environment inside the factory
- [x] 3.2 Verify `RoutedTTSEngine`'s per-engine cache (`engines.py:188`) keys correctly for `fish-audio` and does not leak a stale instance when the model changes

## 4. Validation and presentation

- [x] 4.1 Add `"fish-audio"` to the engine allowlist in `ConfigureTTSUseCase.update_config_async` (`tts_config_use_case.py:54`) and update the rejection message to name all four engines
- [x] 4.2 Add 32-hexadecimal `reference_id` shape validation, applied only when the resolved engine is `fish-audio`, returning a `ConfigureTTSResult` failure that states the expected format
- [x] 4.3 Add a `fish-audio` branch to `_build_fallback_voice_label` (`discord_command_handlers.py:37`) so the voice does not fall through to the `R.E.P.O.` pyttsx3 label
- [x] 4.4 Add a `fish-audio` branch to `_add_voice_resolution_field` (`discord_command_handlers.py:50`) so it does not reach the pyttsx3 branch and call `is_voice_available` against a remote voice ID
- [x] 4.5 Add the matching i18n entry to `src/presentation/discord_i18n` for the new voice-resolution message, in every locale the catalog already supports
- [x] 4.6 Confirm by inspection that `voice_catalog.py`, `settings_gui_dialog.py`, and `settings_console_dialog.py` need no edit, and that Fish is therefore absent from the desktop engine picker

## 5. Tests

- [x] 5.1 Add `test_create_fish_audio_engine` to `tests/unit/infrastructure/test_tts_engines.py`, alongside the three existing factory tests
- [x] 5.2 Test successful synthesis with a mocked `aiohttp` response: asserts the `model` header, the `reference_id` body field, and that an MP3 `AudioFile` is returned
- [x] 5.3 Test the rate mapping at 180 → 1.0, 50 → 0.5 (clamped), and 300 → at most 2.0
- [x] 5.4 Test each of 401, 402, 404, and 422 producing its distinct message, and assert the API key appears in none of them
- [x] 5.5 Test temp-file cleanup on an HTTP error and on cancellation, mirroring `test_generate_audio_cleans_temp_file_after_cancellation`
- [x] 5.6 Test that `language` is absent from the request body
- [x] 5.7 Add settings tests: startup fails when `fish-audio` is selected without `FISH_AUDIO`, succeeds when the key is absent but another engine is selected, and defaults the model to `s2.1-pro-free`
- [x] 5.8 Add config use-case tests: a malformed `voice_id` is rejected for `fish-audio`, a 32-hex value is accepted, and the same value is left unvalidated for other engines
- [x] 5.9 Run the full suite and confirm the coverage threshold in `pyproject.toml` still passes

## 6. Deployment and documentation

- [x] 6.1 Wire `FISH_AUDIO` into `deploy/k8s/base/bot-config.yaml` as a Secret reference, never an inline ConfigMap value, and confirm `.dockerignore` keeps `.env` out of images
- [x] 6.2 Document the engine in the user-facing docs: how to obtain a `reference_id` from fish.audio, the `/config` example, and that the voice must exist in a reachable Fish account
- [x] 6.3 Record the measured billing behavior from `design.md` where operators will find it, so the two-ledger model and the 2026-11-30 date are not rediscovered by probing

## 7. Review gates

- [x] 7.1 Dispatch **Gard** (model: up) for security review: first provider credential in the repository, key handling and non-disclosure, Kubernetes Secret wiring, and the third-party retention of guild members' text
- [ ] 7.2 Resolve open question 1 from `design.md` — whether retention for third-party model training is acceptable, and whether disclosure to guild members is in scope — before merge
- [x] 7.3 Dispatch **Quinn** (model: down) to verify test coverage against the spec's scenarios, in particular the error-classification and cleanup requirements

## 8. Review findings applied

- [x] 8.1 Replace the public-figure voice id with the non-resolving placeholder `0123456789abcdef0123456789abcdef`, above all in the shipped `/config` validation error (Gard P1)
- [x] 8.2 Make credential sanitization structural: autouse fixture in `tests/conftest.py` instead of the opt-in per-file fixture (Gard P1)
- [x] 8.3 Scrub the API key from the relayed provider error body before it reaches the Redis queue item and the OTel span (Gard P2)
- [x] 8.4 `api_key: str = field(default="", repr=False)` so no repr discloses the credential (Gard P2)
- [x] 8.5 Validate `engine` and `voice_id` in the HTTP `/speak` config override, returning 400 (Gard P2)
- [x] 8.6 `allow_redirects=False` on the POST so Authorization cannot follow a cross-origin redirect regardless of the aiohttp floor (Gard P3)
- [x] 8.7 Convert `aiohttp.ClientError` and `TimeoutError` into `FishAudioError` instead of letting a raw transport error reach the caller (Quinn)
- [x] 8.8 Reject a 200 response with an empty stream instead of returning a 0-byte file that plays as silence (Quinn)
- [x] 8.9 Use `fullmatch` on a shared `is_fish_audio_reference_id` helper in `core`; an anchored `$` accepted a trailing newline (Quinn)
- [x] 8.10 Validate the `voice_id` shape at startup when `TTS_ENGINE=fish-audio`; the default `roa/pt-br` booted successfully and failed on the first `/speak` (Quinn)
- [x] 8.11 Add the tests the reviewers named: catalog excludes Fish, desktop picker excludes Fish even if catalogued, no desktop source references Fish, container wiring, `repr` non-disclosure, key-echoing error body, `caplog`, non-JSON and empty and over-long error bodies, transport error and timeout, partial-stream cleanup, reference_id boundaries, HTTP override rejection
- [x] 8.12 Replace the cancellation test's `sleep(0.05)` with an `asyncio.Event` signal so it cannot flake on a loaded CI box (Quinn)
- [x] 8.13 Add the retention clause to `voice_resolution.fish` in both locales and a startup WARN naming the third-party retention (Gard containment)
- [x] 8.14 Fix a pre-existing temp-file leak in the edge-tts test (one 0-byte file per run); verified the Fish tests leak none

## 9. Open, not blocking the diff

- [x] 9.1 **Decided 2026-10-07:** `voice` accepts a raw 32-hex reference_id as a fall-through when it matches no catalog key. Applied to `/config`, `/server-config` and `/speak`; no new command or parameter, per-scope opt-in restored, spec and docs corrected to the real interface.
- [x] 9.2 **Decided 2026-10-07:** retention accepted for this deployment (private server, no formal member notice). Recorded in `design.md`. Containment kept in code: startup WARN plus the clause in the `/config` voice-resolution embed. A public or shared server reopens this.
- [ ] 9.3 Observability for the 402 path before 2026-12-01, when the free model may stop being served. Owner: Pipe.
- [ ] 9.4 Consider an ADR: this is the repository's first third-party provider credential and first egress of user-authored text. Owner: Spencer.
- [ ] 9.5 Extend the conftest credential sanitization to `DISCORD_TOKEN`, `BOT_SPEAK_TOKEN` and `DATABASE_URL`. Gard verified no hazard exists for them today (every test declares them in its tmp `.env`, and `load_dotenv(override=True)` wins), so this is hardening, not a fix.
- [ ] 9.6 Rename `.env.test` to `.env.test.example`, or drop its `.dockerignore` re-allow, so the deny-all's "only examples get in" invariant holds by shape rather than by inspection. Pre-existing.

## 10. Second review round applied

- [x] 10.1 **Bug:** validation stripped the identifier while storage and transmission kept the raw input, so a pasted id with whitespace passed the shape check and was sent to the provider verbatim - the exact failure the check exists to prevent. Replaced the boolean with `normalize_fish_audio_reference_id`, which returns the canonical value, so validation and storage cannot disagree. Fixed in the use case, the HTTP override, both Discord paths and the env read. (Quinn)
- [x] 10.2 Handler-level tests for the fall-through at both call sites: reverting either one to a bare catalog lookup previously left every test green. Covers `/config`, `/server-config`, the strip, rejection, language preservation, catalog-key precedence, and the switch back from Fish to a catalog voice. (Quinn)
- [x] 10.3 **The retention disclosure now reaches `/speak voice:<id>`.** It only rendered in the `/config` embed, and `/speak` deletes its reply on success - so the path members actually use disclosed nothing, leaving the accepted decision untrue. The builder reports `used_supplied_provider_voice` and the handler shows the notice instead of dismissing the reply. New i18n key in both locales. (Gard P1)
- [x] 10.4 Removed the 8-character floor in `_redact_api_key`: it traded confidentiality for readability in the one function whose job is confidentiality. Only the empty key is guarded now, because `str.replace("")` would splice the marker between every character. (Gard P3)
- [x] 10.5 Applied `_redact_api_key` to the transport-error message so the invariant is enforced rather than merely true, and recorded on that line why it formats `{exc}` and never `{exc!r}`: `aiohttp.ClientResponseError`'s repr carries `request_info.headers`, which carries `Authorization`, and that message reaches the Redis queue item and an OTel span. (Gard P3)
- [x] 10.6 Reordered `except TimeoutError` before `except aiohttp.ClientError`: `ServerTimeoutError` subclasses both and was getting the verbose message. (Gard)
- [x] 10.7 Stopped reflecting the caller-supplied engine value into the 400 body and the log line; the message names the field, matching the voice_id branch. A CRLF would otherwise let an authorized caller forge log entries. (Gard P3)
- [x] 10.8 Moved the rate-limit check above the override validation so the reject path costs budget - a single check, not a second one, since `_check_rate_limit` consumes it. (Gard P3)
- [x] 10.9 Strengthened the tests that passed for the wrong reason: the 200 override test now proves the override reached the queue rather than only returning 200; the 400 tests assert no synthesis occurred and that the caller's value is not echoed. (Quinn)
- [x] 10.10 Added the missing override cases: the nested `config_override` form, a voice-only override validated against the stored engine, the strip applied to the override, and a regression that all three keyless engines are still accepted. (Quinn)
- [x] 10.11 Made the catalog test platform-independent (it enumerated Windows voices through pyttsx3), gave `allow_redirects=False` its own named security test, and added empty-key and short-key redaction tests. (Quinn)
- [x] 10.12 Container wiring assertion: the helper being correct did not prove `__init__` passes the settings into `RoutedTTSEngine`. (Quinn)
- [x] 10.13 Strengthened the catalog-key regression in the speak builder to assert language and voice_id, not just engine, because the new branch rebuilds the `TTSConfig`. (Quinn)

## 11. Open, with owners

- [ ] 11.1 **Decide whether any guild member may select any third-party voice from the operator's account.** The fall-through resolved the no-opt-in problem but opened an authorization boundary as a side effect: `/config` has no permission gate, so the impersonation and terms-of-service exposure that was one operator decision is now a lever every member holds, and account termination takes the credential and the engine with it. The accepted retention decision did not cover this. Gard's cheap containment is a `FISH_AUDIO_ALLOW_USER_VOICES`-style flag defaulting to off, which would let the private-server decision stand while making a shared server safe by default. Not built: it is speculative config for a private deployment, and the decision is Scott's on scope and Archie's on contract. **This is the condition on the scope of task 9.2.**
- [ ] 11.2 Observability for the 402 path before 2026-12-01, when the free model may stop being served. Owner: Pipe.
- [ ] 11.3 ADR: first third-party provider credential and first egress of user-authored text in this repository. Owner: Spencer.
- [x] 11.4 Recorded the impersonation exposure in `docs/reference/FISH_AUDIO_TTS.md` under a new "Anyone in a guild can choose the voice" section, naming the account-level consequence and the absence of a switch. (Gard)
- [ ] 11.5 Extend the conftest credential sanitization to the other secrets, renaming the fixture or using a second tuple - `DISCORD_TOKEN` is not a provider credential and a fixture whose name stops describing its contents stops being trusted. Hardening; Gard verified no hazard exists today.
- [ ] 11.6 Rename `.env.test` to `.env.test.example`, or drop its `.dockerignore` re-allow, so the deny-all's "only examples get in" invariant holds by shape. Pre-existing.

## 12. Third review round applied

- [x] 12.1 **Regression I introduced, found while writing the question that would have asked about it.** My `/speak` disclosure replaced the reply instead of adding to it, so a member queued behind others lost their queue position. Now composed: a reply that would otherwise be deleted carries the notice alone; one carrying information the caller needs keeps it and gains the notice underneath. Tested in both directions, including that a catalog voice queued behind others is byte-for-byte unchanged.
- [x] 12.2 Deleted `is_fish_audio_reference_id`. Quinn's structural point stands: a boolean that discards the validated value is the footgun behind both strip bugs. The one caller that genuinely only checks (`Settings.validate`) now writes `normalize_fish_audio_reference_id(...) is None`, so the discard is visible at the call site.
- [x] 12.3 Shape tests now assert the canonical returned value rather than truthiness, and each call site that stores or transmits the identifier asserts the value it hands on is canonical: the use case, `_resolve_voice_selection`, the speak builder's override, the HTTP override, and the env read.
- [x] 12.4 Tests for the rate-limit reorder: an invalid override consumes exactly one unit of budget, and an exhausted budget answers before the 400.
- [x] 12.5 Pinned the `TTS_VOICE_ID` strip at boot with a padded value, including through `validate()`.

**One review claim I rejected.** Quinn reported a live hole in `Settings.validate`: that `TTS_VOICE_ID` is unstripped, so a padded identifier would pass boot validation and be transmitted with whitespace. `settings.py:133` already reads it as `.strip()`, which was added in round 10.1, so the path he described cannot occur. Verified before acting, and task 12.5 now pins it so the claim cannot be made again from a stale reading. His structural recommendation (12.2) was accepted on its own merits.

## 13. Production deploy (GCP e2-micro)

Reviewed by Pipe (plan) and Gard (credential transfer). Two blockers were in the
plan, not the code.

- [x] 13.1 **CI deploy is impossible by design, not broken.** `infra/modules/gcp_bot_host/variables.tf` forbids `0.0.0.0/0` in `ssh_allowed_cidrs` and the firewall applies it to port 22, so a GitHub-hosted runner is dropped - which is why the 2026-08-21 attempt read `Connection timed out`. `docs/deploy/SMALL_CLOUD_VM_DEPLOY.md:427` already said so in writing. `dry_run` cannot detect it: every SSH step is guarded `if: ${{ !inputs.dry_run }}`. Deploy runs by hand over SSH; the workflow's real-deploy path stays unusable until `runs-on` changes. Self-hosted runner rejected: it would spend RAM on a 1 GB host where the bot is already capped at 768m.
- [x] 13.2 **`vm-bootstrap-env.sh` must not be used to add the keys.** It scps the whole local env file over `.env.runtime` with no merge, which would blank `APP_VERSION` and `PREVIOUS_APP_VERSION` - written on the host by `vm-deploy.sh` and shipped empty in `.env.vm.example`. The `PREVIOUS_APP_VERSION` write is guarded by `[ -n "${current_version}" ]`, so it would be skipped and `--rollback` would fail at the moment it is needed. Append in place instead.
- [x] 13.3 `.env.vm.example` gained `FISH_AUDIO` and `FISH_AUDIO_MODEL`; it was the one env example missing them, and the one that feeds this deployment.
- [x] 13.4 **Credential transfer method decided: interactive edit on the host.** Not `ssh host "printf ... >> file"`. On Windows that leaves the key in PSReadLine's `ConsoleHost_history.txt` - a durable plaintext file that reaches backups, not transient scrollback. The stdin-pipe alternative trades it for a local plaintext fragment that cannot be reliably shredded on NTFS. The editor form also makes two silent hazards visible: a file not ending in a newline would concatenate onto `PREVIOUS_APP_VERSION=`, and a duplicate `FISH_AUDIO=` from a retry is last-wins with no warning.
- [x] 13.5 **`rollback.yml` is the wrong gesture for this host** - it runs `docker compose` on the runner against `docker-compose.prod.yml`. The real one is `vm-deploy.sh <explicit tag>`, preferred over `--rollback` because the pointer is fragile (13.2).
- [x] 13.6 **Rollback is not state-clean, and the smoke test manufactures the problem.** `config_storage.py:92` loads `engine` with no allowlist, so an older image reads `fish-audio` and fails only at synthesis - contained (container starts, `/ready` does not probe Fish, other guilds unaffected) but sticky across a rollback. Verifying in Discord persists exactly that state, so the plan now ends by returning the test guild to `gtts`. A rollback sweep must cover `configs/guild_*.json` **and** `configs/guild_*_user_*.json`.
- [x] 13.7 Credential status recorded with dates in `docs/reference/FISH_AUDIO_TTS.md`, including the detection surface (the Fish account's own usage history - there is no local telemetry) and **rotate-before-funding as a precondition**, since the accepted risk is bounded only while the account has no API credit.

### Corrections to the review itself

- Gard argued CRLF could break `APP_VERSION`/`PREVIOUS_APP_VERSION`. It cannot: `read_env_value` in `vm-deploy.sh` ends in `tr -d ''`. The real CRLF victim is `DISCORD_TOKEN`, which `Config` reads with no `strip` (`settings.py:71`) and which reaches the container through Compose's `env_file`, so a whole-file CRLF conversion would fail Discord login. The `cat -A` check stays in the runbook, for that reason instead.
- `FISH_AUDIO` and `FISH_AUDIO_MODEL` are both `.strip()`ed on read, so trailing whitespace on those two lines specifically is harmless.

## 14. Still open

- [ ] 14.1 Observability for the 402, before 2026-12-01. The signal already exists with no new code: `/observability` exposes `error_rate_by_engine` and the telemetry is wired regardless of `OTEL_ENABLED`, while the durable trigger is the log string `requires API credit (402)`. Proportionate control for a **dated** event on a 1 GB host: a calendar reminder for ~2026-11-20 with the action pre-decided, plus a log-grep cron as the backstop for early withdrawal. Note for the runbook: `/ready` deliberately does not probe Fish Audio, so **silence is not health** - until the cron exists, the first report of a 402 comes from a user in Discord. Owner: Pipe.
- [ ] 14.2 `docs/operations/PRODUCTION_RUNBOOKS.md` has no VM rollback procedure and no 402 procedure. The config-reset sweep (13.6) and the "silence is not health" fact both need to be durable. Pre-existing gap this change should not inherit silently. Owner: Spencer.
- [ ] 14.3 `deploy-vm.yml`'s "Report deployed version" step comments that it reads `/version` and `/health`, but it only curls `/health` - which is a static `{"status":"healthy"}` literal and proves nothing about which version is serving. File against the workflow; not in scope here.
- [ ] 14.4 On merge to main, `deploy-bot-windows.yml` fires and its deploy job queues forever against a `[self-hosted, windows, bot-server]` runner that does not exist (`total_count: 0`). Harmless, but cancel the run. Either register the runner or restrict the workflow's trigger.
