# Graph Report - .  (2026-08-07)

## Corpus Check
- 303 files · ~106,266 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3538 nodes · 7714 edges · 177 communities (140 shown, 37 thin omitted)
- Extraction: 87% EXTRACTED · 13% INFERRED · 0% AMBIGUOUS · INFERRED: 1027 edges (avg confidence: 0.58)
- Token cost: 484,600 input · 0 output

## Community Hubs (Navigation)
- Desktop App Configuration
- TTS Queue Orchestrator & Security
- TTS Execution Service
- Core Interfaces & Telemetry
- Redis Audio Queue
- Bot Queue Worker
- Desktop Main Window GUI
- Desktop Hotkey Backend
- TTS Audio Engines
- Bot Settings & Runtime Config
- Config Migration to Postgres
- Desktop TTS Status Gateway
- Interface Language Preferences
- Hotkey Monitoring Service
- Desktop Bot Gateway
- Desktop Discord Bot Client
- Deploy: K8s Observability Metrics
- Discord Voice Channel & FFmpeg
- Architecture Diagrams: Runtime
- Desktop App Lifecycle
- Voice Channel Resolution
- Discord Presenters & Results
- Core Entities & Config
- Discord Voice Channel Interfaces
- Discord Commands Tests
- Desktop HTTP Bot Client
- Discord i18n & Locale
- Desktop GUI Logging
- Pyttsx3 TTS Adapter
- Desktop Config Dialogs
- Speak HTTP Controller
- Deploy Docs: Observability & Rollback
- TTS Voice Catalog GUI
- Speak Use Case Tests
- Discord Command Config
- Config Embed Builder
- Quality Gates & Coverage
- Voice Channel Use Cases
- Dependency Maintenance Script
- Configure TTS Use Case
- Interface Language Discord Commands
- Bot Runtime Container
- Docs: Dependency & Elite Upgrade Plan
- Desktop Config Dialog Helpers
- In-Memory Config Repository
- Fake Redis Audio Queue Tests
- Docs: Release & Runbooks
- Bot Health Endpoints & CI
- TTS Voice Catalog Runtime
- Postgres Config Storage
- Desktop Config Validation
- Initial Setup Dialog
- Voice Runtime Status
- Infrastructure HTTP Server
- Discord.py Dependency Docs
- Rate Limiting
- Runtime Telemetry Spans
- Voice Context Query DTOs
- TTS Fallback Routing
- System Tray Notifications
- Desktop Settings Dialog
- Hotkey Text Capture
- TTS Execution Port
- Bot Readiness Probes
- Desktop App TTS Service
- Mock Audio Queue Tests
- Core Entities Tests
- OpenTelemetry Fake Exporters
- System Tray Notification Service
- Voice Context Controller
- Generated Diagrams: Config Repository
- Desktop TTS Bot Client
- Architecture Reference Docs
- Codacy CI Workflow
- HTTP Speak Presenter
- Docs: Copilot & Architecture Guide
- Discord Speak Request Builder
- Desktop UI Runtime Coordinator
- Desktop App Build Docs
- Threat Model & Rate Limits
- Desktop App Status Builder
- Desktop Discord Bot Client Requests
- HTTP Server Tracing
- Postgres Deploy & Restore Docs
- Desktop UI Configuration Coordinator
- Desktop Config Models
- Notification Service Protocol
- OpenTelemetry Fake Spans
- In-Memory Runtime Telemetry
- ADR: Docker Compose Postgres
- Docs: Baseline & Release Gates
- Bot Readiness DB Ports
- Desktop Config Paths
- OpenTelemetry Audio Queue
- OpenTelemetry Fake Providers
- Deploy: Tempo Tracing
- Clean Architecture Docs
- Generated Diagrams: Bot Main
- Desktop App Status DTOs
- Desktop Config Environment
- Bot-Desktop HTTP Contract Tests
- OpenTelemetry Fake Meters
- Generated Diagrams: Desktop Lifecycle
- Generated Diagrams: Desktop Config
- Manual Integration Check Script
- Desktop Notification Service
- OpenTelemetry Null Span
- GitHub Contributing Guide
- Dependency Maintenance CLI
- Bot Dependency Readiness DTO
- Console Notification Service
- Quality Gates Tests
- ArgoCD GitOps Deploy
- Generated Diagrams: Configure TTS Result
- HTTP Server Observability
- Bot Readiness Chaos & Failure
- Null System Tray Icon
- System Tray Icon Adapter
- Assets: App Icon
- WinSW Windows Service Deploy
- Bot-Desktop HTTP Contract Docs
- Testing Coverage Gate Docs
- Edge-TTS Engine
- Core Timeout Config
- Desktop Config Reconfigure Action
- Manual Discord Connection Test
- Desktop Config Validator
- Architecture Boundary Tests
- OTel Collector Pipeline
- Bot Speak Runtime Flow Docs
- Audio Queue Status Interface
- Observability Stack Services
- System Tray Icon Creation
- Desktop Hotkey Config Model
- Getting Started: Environment Setup
- System Tray Handler Init
- System Tray Stop Handling
- Conftest Temp Paths
- Generated Diagrams: Discord TTS Service
- Generated Diagrams: Desktop Bot Gateway
- Generated Diagrams: TTS Engine Port
- Generated Diagrams: Notification Service
- Generated Diagrams: Keyboard Monitor
- Generated Diagrams: Config Storage
- Contributing: ElevenLabs Engine
- Icon Creation Script
- Application Package Init
- Bot Runtime Package Init
- Core Package Init
- Desktop Package Init
- Desktop Services Package Init
- Discord Infrastructure Package Init
- HTTP Infrastructure Package Init
- Infrastructure Package Init
- Persistence Package Init
- TTS Infrastructure Package Init
- Presentation Package Init
- Tests Package Init
- Unit Tests Package Init
- Generated Diagrams: Hotkey Manager
- Generated Diagrams: HTTP Discord Client
- Generated Diagrams: System Tray Service
- Generated Diagrams: Discord Voice Channel
- Generated Diagrams: HTTP Server
- Generated Diagrams: Voice Context Presenter
- GitHub Scorecard Workflow
- GitHub Security Workflow
- GitHub CodeQL Job
- GitHub Dependency Review Job
- Windows Hotkey Package Metadata

## God Nodes (most connected - your core abstractions)
1. `TTSConfig` - 200 edges
2. `AudioQueueItem` - 117 edges
3. `TTSRequest` - 104 edges
4. `RedisAudioQueue` - 73 edges
5. `InMemoryAudioQueue` - 71 edges
6. `OpenTelemetryRuntime` - 68 edges
7. `AudioFile` - 62 edges
8. `TTSQueueOrchestrator` - 61 edges
9. `DesktopApp` - 61 edges
10. `DesktopAppConfig` - 58 edges

## Surprising Connections (you probably didn't know these)
- `assets/icon.png (project microphone icon)` --conceptually_related_to--> `Distributed TTS System (project)`  [INFERRED]
  assets/icon.png → README.md
- `test_null_system_tray_icon_is_never_available()` --calls--> `NullSystemTrayIcon`  [INFERRED]
  tests/unit/desktop/test_notification_services.py → src/desktop/adapters/system_tray.py
- `test_configuration_repository_returns_defaults_on_invalid_json()` --calls--> `ConfigurationRepository`  [INFERRED]
  tests/unit/desktop/test_desktop_config.py → src/desktop/config/repository.py
- `config/quality_gates.json` --semantically_similar_to--> `Codacy Coverage Threshold (77%)`  [INFERRED] [semantically similar]
  .github/workflows/test.yml → .codacy.yml
- `requirements.txt` --conceptually_related_to--> `pyproject.toml`  [INFERRED]
  .github/workflows/security.yml → docs/maintenance/DEPENDENCY_MAINTENANCE.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **AI Governance Documents Derivative of .specify/** — github_copilot_instructions, github_copilot_workspace_yml, github_instructions_documentation_organization, specify_constitution, specify_readme_md [EXTRACTED 0.90]
- **Release Supply Chain Security Flow (build, scan, sign, attest)** — github_workflows_release_publish_bot_image_job, trivy_critical_vuln_scan_release, cosign_keyless_signing, ghcr_bot_image, dockerfile [EXTRACTED 0.90]
- **CI Quality Gates (format, lint, type-check, coverage)** — github_workflows_test_critical_tests_job, scripts_test_quality_gates_py, config_quality_gates_json, codacy_yml_coverage_threshold [INFERRED 0.85]
- **Kustomize overlays forming environment promotion path (minikube -> staging -> prod)** — deploy_k8s_overlays_minikube, deploy_k8s_overlays_staging, deploy_k8s_overlays_prod, deploy_k8s_base_kustomization [EXTRACTED 0.90]
- **Base bot stack workloads sharing bot-config/bot-secrets** — deploy_k8s_base_bot_deployment, deploy_k8s_base_postgres_statefulset, deploy_k8s_base_redis_statefulset, deploy_k8s_base_bot_config, deploy_k8s_base_bot_secrets [EXTRACTED 0.90]
- **Observability pipeline: Prometheus scrapes, alerts via Alertmanager, visualized in Grafana** — deploy_observability_prometheus, deploy_observability_prometheus_rules, deploy_observability_alertmanager, deploy_observability_grafana_provisioning_datasources_datasources [EXTRACTED 0.90]
- **OpenTelemetry Tracing Pipeline: Bot -> Collector -> Tempo -> Grafana** — docker_compose_prod_bot_service, docker_compose_prod_otel_collector_service, docker_compose_prod_tempo_service, docker_compose_prod_grafana_service, docs_adr_0004_opentelemetry_runtime_observability_decision [INFERRED 0.85]
- **Production Persistence and Queue Coordination: Postgres + Redis backing the Bot** — docker_compose_prod_postgres_service, docker_compose_prod_redis_service, docker_compose_prod_bot_service, docs_adr_0002_postgres_config_storage_decision, docs_adr_0003_redis_backed_queue_coordination_decision [INFERRED 0.85]
- **Desktop Hotkey to Bot Speak HTTP Flow** — docs_architecture_runtime_flows_desktopapphotkeyhandler, docs_architecture_runtime_flows_speaktextexecutionusecase, docs_architecture_runtime_flows_desktopapp_ttsservice, docs_architecture_bot_desktop_http_contract_speak_endpoint, docs_architecture_bot_desktop_http_contract_e2e_test [EXTRACTED 1.00]
- **Layered Clean Architecture: presentation/bot_runtime -> application -> core, with infrastructure implementing core ports** — src_presentation_layer, src_bot_runtime_layer, src_application_layer, src_core_layer, src_infrastructure_layer [EXTRACTED 1.00]
- **Shared TTS speak flow: SpeakTextUseCase, TTSQueueOrchestrator, VoiceChannelResolutionService coordinate via shared core ports** — docs_architecture_diagrams_bot_runtime_speaktextusecase, docs_architecture_diagrams_bot_runtime_ttsqueueorchestrator, docs_architecture_diagrams_generated_core_iaudioqueue, docs_architecture_diagrams_generated_core_ttsrequest [EXTRACTED 1.00]
- **Bundled production stack: bot, otel-collector, Prometheus, Alertmanager, Tempo, Grafana form the observability pipeline** — otel_collector_service, prometheus_service, alertmanager_service, tempo_service, grafana_service [EXTRACTED 1.00]
- **Release Validation Flow (checklist + baseline gates + rollback)** — docs_operations_release_checklist_document, docs_operations_baseline_and_release_gates_guide, docs_operations_dr_drills_guide, config_quality_gates_json [INFERRED 0.85]
- **Supply Chain Provenance Chain (SBOM, scan, sign, attest)** — docs_maintenance_dependency_maintenance_cyclonedx, trivy_scanner, cosign_signing, github_build_provenance_attestation, ghcr_registry [EXTRACTED 1.00]
- **/speak Endpoint Threat Model And Runtime Controls** — speak_endpoint, docs_security_threat_model_runtime_controls, bot_rate_limit_max_requests, bot_rate_limit_window_seconds, docs_security_threat_model_trust_boundaries [EXTRACTED 1.00]

## Communities (177 total, 37 thin omitted)

### Community 0 - "Desktop App Configuration"
Cohesion: 0.04
Nodes (63): DesktopConfigurationApplicationService, Validate, persist, and apply Desktop App configuration side effects., DesktopConfigurationCoordinator, Coordinate configuration edits and their side effects for the Desktop App., Validate, persist, and apply configuration changes from the main window., DesktopApp, Create action coordinators lazily for direct unit-test usage., Wire tray callbacks and hotkey processing to the current services. (+55 more)

### Community 1 - "TTS Queue Orchestrator & Security"
Cohesion: 0.06
Nodes (38): Test the valid scenario where the user is in the bot channel., Test channel with a stable channel id., Test repository for security scenarios., Return the channel where the bot is connected., Return the channel where the user is currently connected., Test the vulnerable scenario where the user moved channels., SecurityTestChannel, SecurityTestRepository (+30 more)

### Community 2 - "TTS Execution Service"
Cohesion: 0.04
Nodes (63): Structured result for Desktop App TTS execution., Execute Desktop App TTS through an explicit Desktop App port., Return whether the underlying TTS service is available., SpeakTextExecutionUseCase, TTSExecutionResult, build_tts_engine_chain(), Shared routing helpers for selecting TTS delivery engines., Order available TTS engines based on the preferred configuration. (+55 more)

### Community 3 - "Core Interfaces & Telemetry"
Cohesion: 0.04
Nodes (56): BotRuntimeObservabilityDTO, Operational snapshot for baseline bot-runtime observability., Input DTO for speak-text use-case boundaries., NullRuntimeSpanContext, Shared observability contracts for application and presentation layers., Speak-text application use case., BotRuntimeTelemetry, NoOpBotRuntimeTelemetry (+48 more)

### Community 4 - "Redis Audio Queue"
Cohesion: 0.07
Nodes (37): AudioQueueItemStatusDTO, AudioQueueStatusDTO, View of a single queued audio item., Queue details for a guild-scoped audio queue., AudioQueueItemStatus, Status of an audio queue item., _build_status_dto(), _item_from_payload() (+29 more)

### Community 5 - "Bot Queue Worker"
Cohesion: 0.04
Nodes (26): Record the outcome of queued playback processing., BotQueueWorker, _default_lock_renew_interval_seconds(), _null_span_context, Protocol, QueueOrchestratorPort, Minimal queue orchestrator behavior needed by the worker., Process the next item for a guild. (+18 more)

### Community 6 - "Desktop Main Window GUI"
Cohesion: 0.06
Nodes (27): DesktopAppMainWindow, DesktopAppMainWindowPresenter, MainWindowMessage, Presentation helpers for the Desktop App main window., View-ready text and color for a main-window status field., Build user-facing messages for the Desktop App main window., Any, Main Desktop App window that keeps configuration, actions, and logs visible. (+19 more)

### Community 7 - "Desktop Hotkey Backend"
Cohesion: 0.05
Nodes (45): Main entry point for the Windows desktop app., DesktopTTSServiceStatusDTO, Runtime status exposed by the Desktop App TTS processor., DesktopConfigurationSaveResultDTO, Structured result for Desktop App configuration saves from the main window., is_keyboard_backend_available(), KeyboardHookBackend, Adapter around the optional keyboard library. (+37 more)

### Community 8 - "TTS Audio Engines"
Cohesion: 0.06
Nodes (41): AudioFile, Represents an audio file path., ITTSEngine, Interface for text-to-speech engines., Generate audio file from text.          Args:             text: Text to convert, Play audio in the voice channel.          Args:             audio: AudioFile to, FileAudioCleanup, Infrastructure helpers for cleaning up generated audio files. (+33 more)

### Community 9 - "Bot Settings & Runtime Config"
Cohesion: 0.05
Nodes (49): _configure_logging(), main(), Main entry point for Discord bot with HTTP server.  This is the refactored versi, run(), _clear_stale_dotenv_values(), Config, _load_environment_snapshot(), Path (+41 more)

### Community 10 - "Config Migration to Postgres"
Cohesion: 0.05
Nodes (40): main(), migrate(), Migrate guild config files from JSON storage into Postgres., GuildConfigRepository, IConfigStorage, JSONConfigStorage, ABC, Any (+32 more)

### Community 11 - "Desktop TTS Status Gateway"
Cohesion: 0.05
Nodes (39): DesktopTTSFlowService, DesktopTTSStatusGateway, DesktopTTSStatusUseCase, Logger, Protocol, Shared Desktop App TTS orchestration helpers., Build Desktop App status information for local/remote TTS availability., Return the typed TTS status for Desktop App runtime views. (+31 more)

### Community 12 - "Interface Language Preferences"
Cohesion: 0.05
Nodes (21): InterfaceLanguagePreferenceRepository, Protocol, Persistence contract for interface language preferences., Return a user's explicit interface language for a guild, if any., Return a guild's explicit default interface language, if any., Persist a user's explicit interface language for a guild., Persist a guild's explicit default interface language., JSONInterfaceLanguagePreferenceRepository (+13 more)

### Community 13 - "Hotkey Monitoring Service"
Cohesion: 0.04
Nodes (36): HotkeyManagerStatusDTO, High-level hotkey manager status., HotkeyHandler, HotkeyService, KeyboardMonitor, ABC, Protocol, Check if currently monitoring. (+28 more)

### Community 14 - "Desktop Bot Gateway"
Cohesion: 0.06
Nodes (30): DesktopBotConnectionStatus, CheckDesktopBotConnectionUseCase, DesktopBotGateway, FetchDesktopBotVoiceContextUseCase, Protocol, Application use cases for Desktop App interactions with the bot runtime., Query the current detected voice context for the configured member., Fetch the current voice context using the injected gateway. (+22 more)

### Community 15 - "Desktop Discord Bot Client"
Cohesion: 0.07
Nodes (34): BotErrorResponseDTO, BotHealthResponseDTO, BotReadinessResponseDTO, BotRuntimeErrorRateDTO, BotSpeakRequestDTO, BotVoiceContextResponseDTO, DiscordVoiceChannelCacheStatsDTO, HotkeyServiceStatusDTO (+26 more)

### Community 16 - "Deploy: K8s Observability Metrics"
Cohesion: 0.06
Nodes (48): bot_queue_age_seconds metric, bot_queue_depth metric, bot_queue_lock_loss_total metric (Redis-backed queue worker), bot_tts_enqueue_to_playback_seconds metric, bot_tts_submissions_total metric, bot-config ConfigMap, bot Deployment, bot-secrets Kubernetes Secret (external) (+40 more)

### Community 17 - "Discord Voice Channel & FFmpeg"
Cohesion: 0.07
Nodes (29): has_ffmpeg_runtime(), _is_usable_executable(), FFmpeg runtime helpers for Discord voice support., Return whether the given path points to an executable file., Return the FFmpeg executable path from env or PATH., Return whether FFmpeg is available for the current process., resolve_ffmpeg_executable(), DiscordVoiceChannel (+21 more)

### Community 18 - "Architecture Diagrams: Runtime"
Cohesion: 0.07
Nodes (46): Bot Runtime Diagram, Note: important architectural handoff is presentation into shared use cases, Desktop Runtime Diagram, Note: DesktopAppUIRuntimeCoordinator owns queued UI actions and main-window lifecycle, Generated Application Diagram (src.application), Generated Core Diagram (src.core), Generated Desktop Runtime Diagram, Generated Infrastructure Diagram (src.infrastructure) (+38 more)

### Community 19 - "Desktop App Lifecycle"
Cohesion: 0.08
Nodes (30): ConfigT, Event, NotificationT, ProcessorT, DesktopAppLifecycleCoordinator, DesktopTTSProcessorLike, HotkeyManagerLike, NotificationServiceLike (+22 more)

### Community 20 - "Voice Channel Resolution"
Cohesion: 0.07
Nodes (18): Record the outcome of a speak request submission., Represents a text-to-speech request., TTSRequest, mock_voice_channel(), MockVoiceChannel, Fixture for mock voice channel., Mock voice channel for testing., Fixture for sample TTS request. (+10 more)

### Community 21 - "Discord Presenters & Results"
Cohesion: 0.11
Nodes (25): CommandTree, JoinVoiceChannelResult, LeaveVoiceChannelResult, Typed application result objects for shared TTS flows., Typed result base for shared application flows., ResultBase, RateLimitResult, Typed result for rate limit decisions. (+17 more)

### Community 22 - "Core Entities & Config"
Cohesion: 0.06
Nodes (24): TTS engine configuration., TTSConfig, Get resolved TTS configuration for a guild/user scope or the global default., Load resolved TTS configuration asynchronously for a guild/user scope or the glo, Set TTS configuration for a specific guild or guild/user scope., Persist TTS configuration asynchronously for a specific guild or guild/user scop, Synchronous audio generation., Get config by guild ID. (+16 more)

### Community 23 - "Discord Voice Channel Interfaces"
Cohesion: 0.06
Nodes (21): Client, IVoiceChannel, Interface for voice channel operations., Connect to the voice channel., Disconnect from the voice channel., Check if connected to voice channel., Get the channel name., Get the guild ID for the voice channel. (+13 more)

### Community 24 - "Discord Commands Tests"
Cohesion: 0.05
Nodes (12): Test DiscordCommands initialization., Test successful /speak command., Test /speak command failure., Test /speak suppresses non-HTTP interaction update failures during shutdown., Test /config command to get current config., Test /config command to update engine., Test /config command failure., Test /join when user is not in voice channel. (+4 more)

### Community 25 - "Desktop HTTP Bot Client"
Cohesion: 0.08
Nodes (25): DesktopBotVoiceContextStatus, Update environment variables from configuration., get_default_discord_bot_url(), Return the default Discord bot URL for the current environment., HttpDiscordBotClient, HTTP adapter for the Discord bot speak endpoint., Check whether HTTP requests can be sent to the bot., Return whether the bot base URL is configured. (+17 more)

### Community 26 - "Discord i18n & Locale"
Cohesion: 0.08
Nodes (22): Locale, locale_str, command_text(), command_translation(), DiscordCommandTranslator, DiscordLocaleResolver, normalize_discord_locale(), Any (+14 more)

### Community 27 - "Desktop GUI Logging"
Cohesion: 0.08
Nodes (23): LogRecord, DesktopBotActionResultDTO, DesktopBotVoiceContextResultDTO, Typed Desktop App result DTOs., Structured result for Desktop App actions against the bot runtime., Structured result for Desktop App voice-context detection., Create and show the main Desktop App window., Desktop App GUI public exports. (+15 more)

### Community 28 - "Pyttsx3 TTS Adapter"
Cohesion: 0.09
Nodes (24): Logger, Pyttsx3Adapter, Thin adapter around pyttsx3 initialization., Return whether pyttsx3 is installed., Create a pyttsx3 engine instance., Create and configure a pyttsx3 engine instance., Generate audio using pyttsx3.          Args:             text: Text to convert, Lazy initialization of pyttsx3 engine. (+16 more)

### Community 29 - "Desktop Config Dialogs"
Cohesion: 0.10
Nodes (15): build_fake_tk_module(), build_fake_ttk_module(), DummyRoot, DummyVar, prevent_real_messageboxes(), test_gui_config_create_tabs_populates_variables(), test_gui_config_handle_voice_selection_updates_fields(), test_gui_config_save_config_saves_valid_configuration() (+7 more)

### Community 30 - "Speak HTTP Controller"
Cohesion: 0.12
Nodes (11): Use case for accepting TTS requests and delegating queued playback., SpeakTextUseCase, Request, Response, Controller for /speak endpoint., SpeakController, test_rate_limit_retry_without_retry_after_keeps_contract_message(), Test SpeakController. (+3 more)

### Community 31 - "Deploy Docs: Observability & Rollback"
Cohesion: 0.08
Nodes (32): deploy/observability/alertmanager.yml, deploy/observability/grafana dashboards and provisioning, deploy/observability/prometheus-rules.yml, deploy/observability/prometheus.yml, deploy/observability/tempo.yaml, deploy/otel/collector-config.yaml, deploy/postgres/001_bot_config_schema.sql, deploy/postgres/002_interface_language_preferences.sql (+24 more)

### Community 32 - "TTS Voice Catalog GUI"
Cohesion: 0.10
Nodes (19): Protocol, Application contracts for exposing user-selectable TTS voice options., Port for listing and resolving user-selectable TTS voices., Return available voice options., Resolve a selectable option by its stable key., Resolve the currently active configuration back to a catalog option., Return whether the configured voice identifier resolves for the engine., TTSCatalog (+11 more)

### Community 33 - "Speak Use Case Tests"
Cohesion: 0.08
Nodes (17): build_speak_use_case(), Factory for SpeakTextUseCase with explicit collaborators., Speak use case should reuse the shared TTS text preparation rules., Speak use case should derive the guild from the member's current voice channel., Test that use case finds channel by channel_id first., Queue overflow should reject the request instead of faking a queued success., Test SpeakTextUseCase., Test successful execution of speak use case. (+9 more)

### Community 34 - "Discord Command Config"
Cohesion: 0.17
Nodes (5): Choice, DiscordSpeakPreparationErrorCode, DiscordCommands, Interaction, Discord slash commands handler.

### Community 35 - "Config Embed Builder"
Cohesion: 0.19
Nodes (10): Embed, ConfigureTTSResult, TTS configuration application use case., _BaseConfigEmbedBuilder, DiscordConfigCommandHandler, DiscordServerConfigCommandHandler, Interaction, Focused handlers for Discord bot command flows. (+2 more)

### Community 36 - "Quality Gates & Coverage"
Cohesion: 0.16
Nodes (27): ParseResult, _build_parser(), _class_matches_path(), _coverage_line_totals(), CoverageDomainGate, CoverageGateConfig, CoverageGateResult, evaluate_coverage_gates() (+19 more)

### Community 37 - "Voice Channel Use Cases"
Cohesion: 0.09
Nodes (14): Public import surface for shared application use cases.  This module is intentio, JoinVoiceChannelUseCase, LeaveVoiceChannelUseCase, Voice-channel related application use cases., Use case for connecting the bot to a member's current voice channel., Use case for disconnecting the bot from a guild voice channel., Test voice channel connection use cases., Join use case should connect to the member channel. (+6 more)

### Community 38 - "Dependency Maintenance Script"
Cohesion: 0.17
Nodes (27): Namespace, build_parser(), build_requirement_report(), command_pin(), command_report(), command_validate(), get_installed_version(), get_outdated_versions() (+19 more)

### Community 39 - "Configure TTS Use Case"
Cohesion: 0.11
Nodes (12): TTSConfigurationData, ConfigureTTSUseCase, Use case for configuring TTS settings per guild., Tests for application use cases., Test ConfigureTTSUseCase., Test getting current configuration., Test updating TTS engine., Test updating TTS language. (+4 more)

### Community 40 - "Interface Language Discord Commands"
Cohesion: 0.09
Nodes (8): ConfigureInterfaceLanguageUseCase, InterfaceLanguagePreferenceResult, Use cases for Discord interface language preferences., Result for interface language preference updates., Delete a user's explicit interface language preference., Delete a guild's explicit default interface language., Configure interface language preferences without changing TTS voice settings., FakeInterfaceLanguagePreferenceRepository

### Community 41 - "Bot Runtime Container"
Cohesion: 0.14
Nodes (13): Container, Sync slash commands only once per process to avoid reconnect churn., Centralize dependency construction and wiring., _build_config(), test_container_requires_redis_dependency_for_redis_backend(), test_container_uses_inmemory_audio_queue_by_default(), test_container_uses_json_storage_when_configured(), test_container_uses_postgres_storage_when_configured() (+5 more)

### Community 42 - "Docs: Dependency & Elite Upgrade Plan"
Cohesion: 0.10
Nodes (26): Argo CD GitOps Application Manifests, BOT_RATE_LIMIT_WINDOW_SECONDS, Cosign Keyless Image Signing, CodeQL Scanning, CycloneDX SBOM Tooling, Dependabot, Dependency Maintenance Guide, pip-audit (+18 more)

### Community 43 - "Desktop Config Dialog Helpers"
Cohesion: 0.13
Nodes (22): Presentation helpers for Desktop App configuration dialogs., build_updated_config(), normalize_optional_text(), prompt_numeric_input(), Return stripped text or None when blank., Return stripped text or fallback when blank., Prompt until the user provides a numeric value or keeps the current one., Validate a numeric text field and return an error message when invalid. (+14 more)

### Community 44 - "In-Memory Config Repository"
Cohesion: 0.10
Nodes (14): InMemoryConfigRepository, Initialize repository with default configuration.          Args:             def, Get resolved TTS configuration for a guild/user scope or the global default., Load configuration asynchronously using the in-memory state., Set TTS configuration for a specific guild or guild/user scope.          Args:, Persist configuration asynchronously using the in-memory state., In-memory configuration storage.      Follows Single Responsibility: only manage, Test getting default configuration. (+6 more)

### Community 46 - "Docs: Release & Runbooks"
Cohesion: 0.09
Nodes (25): Observability Engineering, Release It!, docs/deploy/STAGING_AND_ROLLBACK.md, GET /health Endpoint, GET /observability Endpoint, Environment Rollback, Disaster Recovery Drills Guide, Image-Based Rollback (Rollback Bot Image workflow) (+17 more)

### Community 47 - "Bot Health Endpoints & CI"
Cohesion: 0.09
Nodes (24): Bot /health and /ready endpoints, Cosign keyless image signing, docker-compose.prod.yml, docker-compose.redis.yml, Dockerfile (bot image build), Full Local Production Stack, Optional Redis Queue For The Bot, Phase 5: Infrastructure As Code (+16 more)

### Community 48 - "TTS Voice Catalog Runtime"
Cohesion: 0.14
Nodes (12): A selectable voice option exposed to presentation layers., TTSVoiceOption, Expose runtime-selectable voices for Discord command autocomplete., RuntimeTTSCatalog, mock_tts_catalog(), MockTTSCatalog, Mock catalog for presentation tests that expose voice options., Fixture for mock TTS catalog. (+4 more)

### Community 49 - "Postgres Config Storage"
Cohesion: 0.13
Nodes (8): PostgreSQLConfigStorage, Any, Persist guild-scoped config in Postgres with room for future growth., FakeConnection, FakeCursor, test_postgres_storage_deletes_config(), test_postgres_storage_saves_and_loads_config(), test_postgres_storage_saves_and_loads_user_config()

### Community 50 - "Desktop Config Validation"
Cohesion: 0.10
Nodes (11): Validate the provided Desktop App configuration., Run first-time configuration when required., EnvironmentUpdater, Updates environment variables from configuration., DesktopAppConfig, Main configuration container for the Desktop App., Save configuration to file., Validate configuration and return (is_valid, errors). (+3 more)

### Community 51 - "Initial Setup Dialog"
Cohesion: 0.13
Nodes (13): ConfigDialogsPresenter, DialogFeedback, InitialSetupResult, User-facing dialog feedback., Structured output for the initial Desktop App setup flow., Build dialog messages and form results for Desktop App configuration UIs., InitialSetupGUI, Initial setup dialog flow for the Desktop App. (+5 more)

### Community 52 - "Voice Runtime Status"
Cohesion: 0.10
Nodes (14): Protocol, Application contracts for Discord voice runtime availability., Structured availability details for Discord voice support., Return whether all required runtime dependencies are present., Return the names of missing runtime dependencies., Port for checking whether Discord voice runtime support is available., Return the current runtime availability details., VoiceRuntimeAvailability (+6 more)

### Community 53 - "Infrastructure HTTP Server"
Cohesion: 0.13
Nodes (17): HTTPServer, Application, HTTP server using aiohttp., HTTP server for bot endpoints.      Follows Single Responsibility: only handles, Build aiohttp application with operational and integration endpoints., Version information for the Discord bot and Desktop App., test_bot_health_endpoint_smoke(), Tests for aiohttp HTTP server endpoints. (+9 more)

### Community 54 - "Discord.py Dependency Docs"
Cohesion: 0.13
Nodes (22): discord.py, Testing Guide, Integration Tests (tests/integration), Manual Validation, pyright (typecheck), ruff (lint), Unit Tests (tests/unit), edge-tts (+14 more)

### Community 55 - "Rate Limiting"
Cohesion: 0.18
Nodes (15): Protocol, RateLimiter, RateLimitRequest, Shared rate limiting contracts for runtime entrypoints., Input used by runtimes to check a caller-specific rate limit., Contract implemented by runtime-specific rate limit adapters., InMemoryRateLimiter, In-memory rate limiting adapter for runtime entrypoints. (+7 more)

### Community 56 - "Runtime Telemetry Spans"
Cohesion: 0.14
Nodes (7): AbstractContextManager, NullRuntimeSpan, Any, BaseException, Protocol, RuntimeSpan, RuntimeTelemetry

### Community 57 - "Voice Context Query DTOs"
Cohesion: 0.16
Nodes (11): VoiceContextResult, Input DTO for voice-context queries., Normalized input contract for current voice-context queries., VoiceContextQueryDTO, HTTP controllers for handling web requests., HTTPVoiceContextPresenter, HTTP-specific presentation mapping for typed application results., Map voice-context results to HTTP JSON/status. (+3 more)

### Community 58 - "TTS Fallback Routing"
Cohesion: 0.10
Nodes (13): Logger, Protocol, Contract for Desktop App delivery engines used by the fallback chain., Speak the provided text., Return whether the engine can be used., Optional delivery-engine extension that exposes a failure reason., Return the latest human-friendly engine error when available., Try engines in order until one succeeds. (+5 more)

### Community 59 - "System Tray Notifications"
Cohesion: 0.12
Nodes (11): PySystemTrayIcon, Hide system tray icon., pystray adapter is available when constructed., Return whether the tray event loop is running., pystray-backed system tray adapter., Set callback handlers for tray actions., test_null_system_tray_icon_is_never_available(), test_py_system_tray_icon_quit_with_handler_delegates_without_hiding() (+3 more)

### Community 60 - "Desktop Settings Dialog"
Cohesion: 0.21
Nodes (3): GUIConfig, Any, GUI configuration interface.

### Community 61 - "Hotkey Text Capture"
Cohesion: 0.13
Nodes (10): HotkeyCaptureResult, HotkeyTextCaptureSession, Pure hotkey text-capture state used by the Desktop App keyboard monitor., Structured result produced when a capture session is completed., Track buffered text between configured trigger keys., Clear current recording state., Consume a key press and return a completed capture when available., test_hotkey_capture_session_ignores_empty_capture_and_reset_clears_state() (+2 more)

### Community 62 - "TTS Execution Port"
Cohesion: 0.12
Nodes (12): DesktopTTSExecutionPort, Protocol, Shared execution services for TTS flows., Port for Desktop App TTS execution and status reporting., Execute speech for the provided normalized text., Return whether the underlying TTS flow is available., Return runtime status details for the Desktop App., Return the latest execution error when available. (+4 more)

### Community 63 - "Bot Readiness Probes"
Cohesion: 0.15
Nodes (16): AudioQueueHealthPort, BotReadinessConfig, ConfigRepositoryHealthPort, ConfigStorageHealthPort, DiscordClientReadinessPort, Protocol, QueueWorkerReadinessPort, Readiness checks for the Discord bot runtime. (+8 more)

### Community 64 - "Desktop App TTS Service"
Cohesion: 0.10
Nodes (9): Check if pyttsx3 is available., Check if Discord TTS is available., Check if TTS service is available., Return whether the Discord bot transport is currently usable., Return whether the configured local engine is available., Return whether the bot client transport dependency is installed., Remove typed characters from the active window., Initialize the pyttsx3 engine. (+1 more)

### Community 65 - "Mock Audio Queue Tests"
Cohesion: 0.10
Nodes (8): mock_audio_queue(), MockAudioQueue, Mock audio queue for testing., Remove and return next item., Persist in-memory item updates for tests., Renew a mock guild lock., Clear completed items., Fixture for mock audio queue.

### Community 66 - "Core Entities Tests"
Cohesion: 0.10
Nodes (12): Tests for core entities., Test creating TTSRequest with all fields., Test AudioFile string representation., Test creating TTSRequest with only text., Test TTSRequest equality comparison., Test TTSRequest string representation., Test TTSRequest entity., Test AudioFile entity. (+4 more)

### Community 67 - "OpenTelemetry Fake Exporters"
Cohesion: 0.14
Nodes (11): _FakeMetricExporter, _FakeMetricReader, _FakePropagate, _FakeResource, _FakeSpanExporter, _FakeSpanKind, _FakeSpanProcessor, _FakeStatus (+3 more)

### Community 68 - "System Tray Notification Service"
Cohesion: 0.14
Nodes (14): System tray availability and runtime status., SystemTrayStatusDTO, Start system tray service only after startup is confirmed., Run system tray (blocking call)., Check if system tray support exists in the environment., Check if the tray loop is actually running., Get system tray service status., Service for managing system tray functionality. (+6 more)

### Community 69 - "Voice Context Controller"
Cohesion: 0.18
Nodes (8): GetCurrentVoiceContextUseCase, Use case for discovering the member's current voice context., Controller for querying the current voice context for a member., VoiceContextController, _FakeSpan, _FakeSpanContext, Tests for HTTP controllers., TestVoiceContextController

### Community 70 - "Generated Diagrams: Config Repository"
Cohesion: 0.11
Nodes (18): IConfigRepository (bot config persistence abstraction), TTSQueueOrchestrator, AudioFile, IAudioFileCleanup, IConfigRepository, ITTSEngine, IVoiceChannel, IVoiceChannelRepository (+10 more)

### Community 71 - "Desktop TTS Bot Client"
Cohesion: 0.12
Nodes (11): AudioDevice, DesktopTTSBotClient, Protocol, Send text to the Discord bot for TTS., Protocol for audio device selection., Set the output device for audio playback., Minimal bot-client behavior needed by Desktop App TTS delivery., Return whether the bot client can send requests. (+3 more)

### Community 72 - "Architecture Reference Docs"
Cohesion: 0.12
Nodes (17): Building Evolutionary Architectures, Clean Architecture, Clean Code, Design Patterns: Elements of Reusable Object-Oriented Software (GoF), Designing Data-Intensive Applications, Enterprise Integration Patterns, Fundamentals Of Software Architecture, Grokking Algorithms (+9 more)

### Community 73 - "Codacy CI Workflow"
Cohesion: 0.12
Nodes (15): CODACY_PROJECT_TOKEN secret, Bandit Engine, Codacy Coverage Threshold (77%), Prospector Engine, Pylint Engine, config/quality_gates.json, scripts/test/quality_gates.py, codacy_cli_analyze mandatory post-edit rule (+7 more)

### Community 74 - "HTTP Speak Presenter"
Cohesion: 0.19
Nodes (5): SpeakTextResult, HTTPSpeakPresenter, Map speak results to HTTP text and status., test_desktop_client_posts_speak_request_to_bot_http_endpoint(), TestHTTPSpeakPresenter

### Community 75 - "Docs: Copilot & Architecture Guide"
Cohesion: 0.23
Nodes (14): docs/architecture/ARCHITECTURE.md, docs/deploy/DEPLOYMENT_GUIDE.md, docs/desktop/DESKTOP_APP_GUIDE.md, docs/getting-started/SETUP.md, docs/getting-started/TESTING.md, docs/README.md, docs/security/THREAT_MODEL.md, GitHub Copilot Instructions (+6 more)

### Community 76 - "Discord Speak Request Builder"
Cohesion: 0.17
Nodes (11): DiscordSpeakPreparationResult, DiscordSpeakRequestBuilder, Protocol, Application service for preparing Discord speak-command input., Prepared speak input or a user-facing validation error., Minimal config lookup needed to build a speak request., Return the effective TTS config for a guild/user., Build speak-command input from Discord interaction primitives. (+3 more)

### Community 77 - "Desktop UI Runtime Coordinator"
Cohesion: 0.18
Nodes (11): DesktopAppUIRuntimeCoordinator, Queue, Queue a UI action to run on the main thread., Run all queued UI actions without blocking the Tk main loop., Own Desktop App window state, queued UI actions, and tray-triggered UI flows., test_ui_runtime_coordinator_drains_queued_actions(), test_ui_runtime_coordinator_handle_configure_focuses_existing_window(), test_ui_runtime_coordinator_queues_actions() (+3 more)

### Community 78 - "Desktop App Build Docs"
Cohesion: 0.16
Nodes (15): app.py (desktop app entrypoint), dist/HotkeyTTS.exe, dist/HotkeyTTS.exe, ARCHITECTURE.md, BOT_DESKTOP_HTTP_CONTRACT.md, Desktop App Guide, Channel discovery priority: connected channel, user ID lookup, error, UX Guidelines: responsive GUI, non-blocking handlers, no absorbed business rules (+7 more)

### Community 79 - "Threat Model & Rate Limits"
Cohesion: 0.16
Nodes (15): BOT_RATE_LIMIT_MAX_REQUESTS, DISCORD_TOKEN, GET /ready Endpoint, Phase 3: Runtime Security, Abuse Cases, Runtime Threat Model, Logging Rules (no secrets/tokens/full payloads), Required Runtime Controls for /speak (+7 more)

### Community 80 - "Desktop App Status Builder"
Cohesion: 0.18
Nodes (11): DesktopTTSProcessorStatusPort, HotkeyManagerStatusPort, NotificationServiceStatusPort, Protocol, Contract needed to determine Desktop App hotkey activity., Return whether hotkey monitoring is active., Contract needed to determine Desktop App TTS availability., Return the typed TTS runtime status. (+3 more)

### Community 81 - "Desktop Discord Bot Client Requests"
Cohesion: 0.13
Nodes (9): DiscordBotClient, Protocol, Port for sending TTS requests to the Discord bot runtime., Return whether the bot client is ready for requests., Build a speak request from the provided text., Send a speak request to the Discord bot., Check whether the bot runtime is reachable., Fetch the current voice context for the configured member. (+1 more)

### Community 82 - "HTTP Server Tracing"
Cohesion: 0.19
Nodes (6): _null_span_context, Request, Response, Health check endpoint for container and runtime probes., Expose a compact runtime observability snapshot for operational baselines., Readiness endpoint that checks configured external dependencies.

### Community 83 - "Postgres Deploy & Restore Docs"
Cohesion: 0.14
Nodes (14): docker-compose.postgres.yml, docs/deploy/BACKUP_AND_RESTORE_DATABASE.md, Local Bot Storage (JSON vs Postgres), Future Runtime Chaos Drills, Postgres Restore Drill, pg_restore, scripts/dev.ps1, Scripts Directory README (+6 more)

### Community 84 - "Desktop UI Configuration Coordinator"
Cohesion: 0.21
Nodes (8): ConfigurationCoordinatorLike, HotkeyManagerLike, Protocol, Handle configure requests from tray or fallback UI flow., Contract needed for configure flows triggered from the tray., Return whether hotkeys are active., Contract for the tray-triggered configuration flow., Run the configuration flow and return the updated config.

### Community 85 - "Desktop Config Models"
Cohesion: 0.26
Nodes (9): DiscordConfig, NetworkConfig, Discord bot configuration., Network configuration., ConfigurationRepository, Any, Repository for configuration persistence., Load configuration from file or create default. (+1 more)

### Community 86 - "Notification Service Protocol"
Cohesion: 0.15
Nodes (8): Protocol, Create appropriate system tray icon based on availability., Protocol for system tray functionality., Show the system tray icon., Set the tooltip text., Check if system tray is available., Check if the tray loop is running., SystemTrayIcon

### Community 87 - "OpenTelemetry Fake Spans"
Cohesion: 0.14
Nodes (4): _FakeSpan, _FakeStartedSpan, _FakeTracer, test_disabled_runtime_span_contexts_are_noops()

### Community 88 - "In-Memory Runtime Telemetry"
Cohesion: 0.26
Nodes (4): deque, InMemoryBotRuntimeTelemetry, Track a compact rolling baseline of bot runtime metrics., test_runtime_observability_snapshot_is_empty_when_no_data_exists()

### Community 89 - "ADR: Docker Compose Postgres"
Cohesion: 0.26
Nodes (13): 001_bot_config_schema.sql Init Script, Postgres-only Compose Service, 001_bot_config_schema.sql Init Script (prod), Production Postgres Service, Production Redis Service, Redis-only Compose Service, ADR 0001: Record Architecture Decisions, ADR 0002: Use Postgres For Production Bot Configuration (+5 more)

### Community 90 - "Docs: Baseline & Release Gates"
Cohesion: 0.18
Nodes (13): Branch Protection Expectation, Chaos Testing Guide, Phase 4: Advanced Test Coverage, Load Testing Guide, Queue Load Baseline Non-Blocking Rationale, Mutation CI Limitation (src.* import path incompatibility), Mutation Testing Guide, mutmut (mutation testing tool) (+5 more)

### Community 91 - "Bot Readiness DB Ports"
Cohesion: 0.17
Nodes (5): Self, DatabaseConnectionPort, DatabaseCursorPort, Minimal DB cursor surface used by readiness pings., Minimal DB connection/context-manager surface.

### Community 92 - "Desktop Config Paths"
Cohesion: 0.18
Nodes (9): get_config_directory(), Path, Get configuration directory following OS best practices., Path, test_configuration_repository_loads_defaults_when_file_missing(), test_configuration_repository_returns_defaults_on_invalid_json(), test_configuration_repository_save_and_load_roundtrip(), test_get_config_directory_windows() (+1 more)

### Community 94 - "OpenTelemetry Fake Providers"
Cohesion: 0.18
Nodes (4): _FakeMeterProvider, _FakeProvider, _FakeTracerProvider, test_shutdown_flushes_meter_and_tracer_providers()

### Community 95 - "Deploy: Tempo Tracing"
Cohesion: 0.20
Nodes (12): Tempo Local Trace Storage Backend, Tempo Metrics Generator, Tempo Distributed Tracing Config, OpenTelemetry Collector Config, alertmanager_discord_webhook_url Secret, Production Alertmanager Service, Production Discord Bot Service, Production Grafana Service (+4 more)

### Community 96 - "Clean Architecture Docs"
Cohesion: 0.23
Nodes (12): Clean Architecture / SOLID Principles, Layer Dependency Rules, DesktopAppConfig Dataclass, Architecture Diagrams Guide, Generated Architecture Diagrams Entry, pyreverse Diagram Curation Workflow, Architecture Transitions Guide, Explicit Contracts Guide (DTO vs Protocol vs dict) (+4 more)

### Community 97 - "Generated Diagrams: Bot Main"
Cohesion: 0.26
Nodes (12): BotMain, Config (bot runtime), Container (composition root), DiscordCommands, HTTPServer (bot), SpeakController, SpeakTextUseCase, VoiceContextController (+4 more)

### Community 98 - "Desktop App Status DTOs"
Cohesion: 0.20
Nodes (8): DesktopAppRuntimeStatusDTO, Aggregated Desktop App runtime status for tray and UI consumers., Get a compact view of current runtime status., NotificationInfoPort, UI runtime coordination for the Desktop App., Show current app status via the main window or tray notifications., Contract needed to show tray status notifications., Show an informational notification.

### Community 99 - "Desktop Config Environment"
Cohesion: 0.20
Nodes (8): DesktopConfigEnvironment, DesktopConfigRepository, Protocol, Port for Desktop App configuration persistence., Persist the provided Desktop App configuration., Port for synchronizing Desktop App configuration into the environment., Synchronize runtime environment variables from configuration., Persist configuration and apply its runtime side effects.

### Community 100 - "Bot-Desktop HTTP Contract Tests"
Cohesion: 0.27
Nodes (11): Application, StreamResponse, _route(), _speak_request(), test_health_and_readiness_contracts_are_json(), test_speak_contract_accepts_authenticated_json_request(), test_speak_contract_rejects_invalid_content_type(), test_speak_contract_rejects_missing_auth_token() (+3 more)

### Community 101 - "OpenTelemetry Fake Meters"
Cohesion: 0.23
Nodes (5): _FakeCounter, _FakeHistogram, _FakeMeter, test_runtime_records_tts_submission_and_latency_metrics(), test_runtime_stays_disabled_when_otel_imports_are_unavailable()

### Community 102 - "Generated Diagrams: Desktop Lifecycle"
Cohesion: 0.18
Nodes (11): DesktopApp, DesktopAppLifecycleCoordinator, DesktopAppTTSProcessor, DesktopAppTTSService, DesktopAppUIRuntimeCoordinator, DesktopMain, DesktopTTSExecutionPort, HotkeyManager (+3 more)

### Community 103 - "Generated Diagrams: Desktop Config"
Cohesion: 0.18
Nodes (11): ConfigInterface, ConsoleConfig, DesktopAppConfig, GUIConfig, Environment Configuration, OpenTofu as default IaC tool, Kubernetes optional (k3s/Minikube), .env.example, .env.prod.example (+3 more)

### Community 104 - "Manual Integration Check Script"
Cohesion: 0.25
Nodes (10): main(), Test the configured Discord bot endpoint when DISCORD_BOT_URL is set., Check whether required release files exist., Compile the desktop entry point without executing GUI code., Run all manual integration checks., Check whether required and optional runtime packages are installed., test_basic_functionality(), test_dependencies() (+2 more)

### Community 105 - "Desktop Notification Service"
Cohesion: 0.18
Nodes (7): NotificationService, ABC, Abstract interface for notification services., Show an informational notification., Show a success notification., Show an error notification., Check if notification service is available.

### Community 106 - "OpenTelemetry Null Span"
Cohesion: 0.33
Nodes (3): _NullSpan, Any, BaseException

### Community 107 - "GitHub Contributing Guide"
Cohesion: 0.22
Nodes (8): Clean Architecture (project structure), Dependency Rule (Presentation -> Application -> Domain <- Infrastructure), SOLID Principles, SpeakController (anti-pattern example: business logic in Presentation), SpeakTextUseCase (anti-pattern example: importing Infrastructure into Application), TTSRequest (anti-pattern example: Domain coupled to discord.Client), Non-negotiable Repository Rules, .specify/ (canonical repository rules)

### Community 108 - "Dependency Maintenance CLI"
Cohesion: 0.27
Nodes (7): MonkeyPatch, Path, test_get_outdated_versions_returns_empty_dict_for_invalid_json(), test_rewrite_requirement_lines_preserves_environment_marker(), test_rewrite_requirement_lines_preserves_inline_comment(), test_run_command_dispatches_unit_tests(), test_validate_command_rejects_arbitrary_python_executable()

### Community 109 - "Bot Dependency Readiness DTO"
Cohesion: 0.29
Nodes (4): BotDependencyReadinessDTO, Readiness state for one bot runtime dependency., Return whether the Discord client is connected and ready., Return whether queue processing is active.

### Community 110 - "Console Notification Service"
Cohesion: 0.20
Nodes (3): ConsoleNotificationService, Console-based notification service., test_console_notification_service_is_available()

### Community 111 - "Quality Gates Tests"
Cohesion: 0.24
Nodes (4): Path, test_evaluate_coverage_gates_aggregates_domain_paths(), test_evaluate_coverage_gates_requires_all_configured_paths(), test_run_observability_gate_accepts_utf8_bom_payload()

### Community 112 - "ArgoCD GitOps Deploy"
Cohesion: 0.28
Nodes (9): bot-secrets runtime Secret, prod-application.yaml (ArgoCD Application), Argo CD GitOps README, staging-application.yaml (ArgoCD Application), deploy/k8s/overlays/* (Kustomize overlays), Infrastructure (iac.yml) workflow, GitOps Promotion via Git overlay newTag change, infra/environments/* (OpenTofu environments) (+1 more)

### Community 113 - "Generated Diagrams: Configure TTS Result"
Cohesion: 0.22
Nodes (9): ConfigureTTSResult, JoinVoiceChannelResult, LeaveVoiceChannelResult, ResultBase, SpeakTextResult, TTSConfigurationData, VoiceContextResult, DiscordSpeakPresenter (+1 more)

### Community 114 - "HTTP Server Observability"
Cohesion: 0.25
Nodes (6): ObservabilitySnapshotProvider, ReadinessProvider, RequestHandler, _append_vary_origin(), StreamResponse, Initialize HTTP server.          Args:             speak_handler: Handler for /s

### Community 115 - "Bot Readiness Chaos & Failure"
Cohesion: 0.56
Nodes (8): BotReadinessProbe, Evaluate whether the bot runtime is ready to receive production traffic., _config(), _dependency(), test_readiness_reports_not_ready_when_postgres_connect_method_is_missing(), test_readiness_reports_not_ready_when_postgres_is_unavailable(), test_readiness_reports_not_ready_when_queue_worker_is_stopped(), test_readiness_reports_not_ready_when_redis_ping_raises()

### Community 116 - "Null System Tray Icon"
Cohesion: 0.22
Nodes (3): NullSystemTrayIcon, Null object used when no tray implementation is available., test_system_tray_service_start_returns_false_when_unavailable()

### Community 117 - "System Tray Icon Adapter"
Cohesion: 0.22
Nodes (3): Abstractable base for system tray adapters., Set callback handlers for tray actions., SystemTrayIconAdapter

### Community 118 - "Assets: App Icon"
Cohesion: 0.29
Nodes (8): assets/icon.png (project microphone icon), Bot HTTP API (/speak, /health, /ready), Discord Bot (runtime app), Distributed TTS System (project), Observability Stack (OpenTelemetry, Prometheus, Grafana), Persistence (JSON local / Postgres production), Queue Layer (in-memory / Redis-backed), Windows Desktop App (runtime app)

### Community 119 - "WinSW Windows Service Deploy"
Cohesion: 0.32
Nodes (8): deploy/winsw/install-or-update-service.ps1, deploy/winsw/tts-discord-bot.xml, Windows Bot Deploy With WinSW, Note: WinSW does not auto-update code; requires explicit deploy step (manual, scheduled, or CI/CD), Deploy Discord Bot to Windows Server workflow, .github/workflows/deploy-bot-windows.yml, Windows Service tts-discord-bot, WinSW (Windows service wrapper)

### Community 120 - "Bot-Desktop HTTP Contract Docs"
Cohesion: 0.25
Nodes (8): BOT_SPEAK_TOKEN Auth Requirement, test_desktop_to_bot_speak_flow.py, Bot/Desktop HTTP Contract, GET /health Endpoint, POST /speak Endpoint, test_bot_desktop_http_contract.py, GET /voice-context Endpoint, DesktopAppTTSService

### Community 121 - "Testing Coverage Gate Docs"
Cohesion: 0.25
Nodes (8): Coverage Gate (80% -> 85%), Queue Critical Domain Coverage Gate (>=80%), Runtime Observability Critical Domain Coverage Gate (>=95%), src/application/runtime_telemetry.py, src/application/tts_queue_orchestrator.py, src/bot_runtime/queue_worker.py, src/infrastructure/audio_queue.py, src/infrastructure/runtime_observability.py

### Community 122 - "Edge-TTS Engine"
Cohesion: 0.29
Nodes (5): Future, _cleanup_temp_audio_file_when_done(), _create_temp_audio_path(), Generate audio using Google TTS.          Args:             text: Text to conver, _remove_temp_audio_file()

### Community 123 - "Core Timeout Config"
Cohesion: 0.29
Nodes (5): Shared timeout defaults used across bot and desktop runtimes., get_default_bot_speak_token(), InterfaceConfig, Return the optional shared token used by Desktop App calls to /speak., Interface configuration.

### Community 124 - "Desktop Config Reconfigure Action"
Cohesion: 0.29
Nodes (5): Open configuration UI and apply changes from the tray flow., NotificationFeedbackPort, Contract used to show configuration feedback., Show an error notification., Show a success notification.

### Community 125 - "Manual Discord Connection Test"
Cohesion: 0.38
Nodes (6): load_env_file(), main(), Load the first available .env file from common local locations., Send a request to the Discord bot the same way the Desktop App does., Run the manual Discord connection check., test_discord_request()

### Community 126 - "Desktop Config Validator"
Cohesion: 0.29
Nodes (5): Return whether the Desktop App has minimum required configuration., ConfigurationValidator, Validates configuration values., Check if minimum configuration is present., test_configuration_validator_is_configured_requires_member_id()

### Community 127 - "Architecture Boundary Tests"
Cohesion: 0.52
Nodes (6): _find_forbidden_imports(), _iter_python_files(), _matches_forbidden_prefix(), test_application_layer_does_not_import_infrastructure(), test_clean_architecture_layers_keep_inward_dependency_flow(), test_presentation_layer_does_not_import_infrastructure()

### Community 128 - "OTel Collector Pipeline"
Cohesion: 0.33
Nodes (6): Tempo OTLP Receiver (http/grpc), Metrics Pipeline (otlp -> prometheus), Collector OTLP Receiver (http/grpc), Prometheus Metrics Exporter, OTLP/Tempo Trace Exporter, Traces Pipeline (otlp -> tempo)

### Community 129 - "Bot Speak Runtime Flow Docs"
Cohesion: 0.40
Nodes (6): Bot /speak Shared Flow, Desktop Hotkey-to-Speech Flow, DesktopAppHotkeyHandler, DiscordCommands, SpeakTextExecutionUseCase, SpeakTextUseCase

### Community 130 - "Audio Queue Status Interface"
Cohesion: 0.33
Nodes (4): AudioQueueStatusView, Protocol, Core-facing view of queue status without depending on application DTOs., Get current queue status for a guild.          Args:             guild_id: Guild

### Community 131 - "Observability Stack Services"
Cohesion: 0.50
Nodes (5): Alertmanager, Grafana, otel-collector service, Prometheus, Tempo

### Community 133 - "Desktop Hotkey Config Model"
Cohesion: 0.40
Nodes (4): HotkeyConfig, Hotkey configuration., Get formatted hotkey display string., test_hotkey_config_keys_property()

### Community 134 - "Getting Started: Environment Setup"
Cohesion: 0.50
Nodes (4): Environment Setup Guide, FFmpeg (Discord voice flow), uv (lockfile dependency sync), .venv Virtual Environment

### Community 139 - "Generated Diagrams: Discord TTS Service"
Cohesion: 0.67
Nodes (3): DiscordTTSService, LocalPyTTSX3Engine, TTSEngine (desktop interface)

## Ambiguous Edges - Review These
- `Provider Adoption Rule` → `render.yaml`  [AMBIGUOUS]
  render.yaml · relation: conceptually_related_to

## Knowledge Gaps
- **186 isolated node(s):** `tts-hotkey-windows`, `Pylint Engine`, `Bandit Engine`, `Prospector Engine`, `SOLID Principles` (+181 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **37 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Provider Adoption Rule` and `render.yaml`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `TTSConfig` connect `Core Entities & Config` to `Desktop App Configuration`, `TTS Queue Orchestrator & Security`, `Audio Queue Status Interface`, `Core Interfaces & Telemetry`, `Redis Audio Queue`, `Bot Queue Worker`, `Desktop Hotkey Config Model`, `Desktop Hotkey Backend`, `TTS Audio Engines`, `Bot Settings & Runtime Config`, `Config Migration to Postgres`, `Desktop TTS Status Gateway`, `Hotkey Monitoring Service`, `Desktop Discord Bot Client`, `Voice Channel Resolution`, `Discord Voice Channel Interfaces`, `Desktop HTTP Bot Client`, `Pyttsx3 TTS Adapter`, `Speak HTTP Controller`, `In-Memory Config Repository`, `TTS Voice Catalog Runtime`, `Postgres Config Storage`, `Desktop Config Validation`, `Voice Context Query DTOs`, `Mock Audio Queue Tests`, `Core Entities Tests`, `System Tray Notification Service`, `Voice Context Controller`, `Discord Speak Request Builder`, `Desktop Discord Bot Client Requests`, `Desktop Config Models`, `Desktop App Status DTOs`, `Bot Dependency Readiness DTO`, `Edge-TTS Engine`, `Core Timeout Config`?**
  _High betweenness centrality (0.256) - this node is a cross-community bridge._
- **Why does `DesktopAppConfig` connect `Desktop Config Validation` to `Desktop App Configuration`, `TTS Execution Service`, `Desktop Main Window GUI`, `Desktop Hotkey Backend`, `Hotkey Monitoring Service`, `Desktop Bot Gateway`, `Core Entities & Config`, `Desktop HTTP Bot Client`, `Desktop GUI Logging`, `Desktop Config Dialog Helpers`, `System Tray Notifications`, `Desktop Settings Dialog`, `Desktop TTS Bot Client`, `Desktop App Status Builder`, `Desktop UI Configuration Coordinator`, `Desktop Config Models`, `Notification Service Protocol`, `Desktop Config Paths`, `Desktop Config Environment`, `Core Timeout Config`, `Desktop Config Reconfigure Action`, `Desktop Config Validator`?**
  _High betweenness centrality (0.062) - this node is a cross-community bridge._
- **Why does `OpenTelemetryRuntime` connect `OpenTelemetry Audio Queue` to `TTS Queue Orchestrator & Security`, `Core Interfaces & Telemetry`, `Redis Audio Queue`, `Bot Queue Worker`, `Voice Channel Use Cases`, `OpenTelemetry Fake Meters`, `OpenTelemetry Fake Exporters`, `Bot Runtime Container`, `OpenTelemetry Null Span`, `Voice Context Controller`, `HTTP Server Observability`, `HTTP Server Tracing`, `Speak HTTP Controller`, `Infrastructure HTTP Server`, `OpenTelemetry Fake Spans`, `OpenTelemetry Fake Providers`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `TTSConfig` (e.g. with `DiscordSpeakPreparationResult` and `DiscordSpeakRequestBuilder`) actually correct?**
  _`TTSConfig` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `AudioQueueItem` (e.g. with `SpeakTextUseCase` and `BotRuntimeTelemetry`) actually correct?**
  _`AudioQueueItem` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `TTSRequest` (e.g. with `SpeakTextUseCase` and `BotRuntimeTelemetry`) actually correct?**
  _`TTSRequest` has 34 INFERRED edges - model-reasoned connections that need verification._