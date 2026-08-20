# Graph Report - python-tts  (2026-08-20)

## Corpus Check
- 262 files · ~106,468 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 3982 nodes · 7798 edges · 465 communities (162 shown, 303 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 965 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be366afc`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

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
- Scripts Directory
- __init__.py
- .is_connected
- DiscordVoiceChannelRepository
- Runtime Flows
- Release Checklist
- README.md
- Elite Upgrade Implementation Plan
- InterfaceLanguagePreferenceRepository
- settings.py
- Deployment Guide
- interface_language_preferences.py
- .handle
- Docker + Postgres + Redis Deploy
- Project Rules
- queue_worker.py
- Backup And Restore Database
- Desktop App Guide
- Codacy Rules
- PULL_REQUEST_TEMPLATE.md
- ConfigDialogsPresenter
- Explicit Contracts Guide
- Shared Vs Runtime-Only Decision Guide
- Staging And Rollback
- Windows Build Guide
- Bot/Desktop HTTP Contract
- Environment Configuration
- Baseline And Release Gates
- Documentation
- server.py
- Kubernetes Manifests
- Architecture Transitions
- DummyTextWidget
- Mutation Testing
- .get_channel_id
- ui_runtime.py
- Documentation Organization
- .get_last_error_message
- DummyWidget
- .__init__
- .test_initialization
- .test_handle_speak_command_success
- .test_handle_speak_missing_dependencies
- .test_handle_speak_failure
- .test_handle_speak_shutdown_fallback_ignores_non_http_send_errors
- .test_handle_config_update_engine
- .test_handle_config_failure
- .test_handle_leave_not_connected
- Argo CD GitOps Application Manifests
- BOT_RATE_LIMIT_MAX_REQUESTS
- BOT_RATE_LIMIT_WINDOW_SECONDS
- bot-secrets runtime Secret
- IConfigRepository (bot config persistence abstraction)
- Cosign Keyless Image Signing
- Docker Compose as default runtime path
- Argo CD applications (GitOps)
- Kustomize file-loading restriction requires duplicated postgres initdb SQL
- Promote via immutable GHCR tag / rollback via Git revert
- deploy/observability/alertmanager.yml
- deploy/observability/grafana dashboards and provisioning
- deploy/observability/prometheus-rules.yml
- deploy/observability/prometheus.yml
- deploy/observability/tempo.yaml
- deploy/otel/collector-config.yaml
- deploy/postgres/001_bot_config_schema.sql
- deploy/postgres/002_interface_language_preferences.sql
- deploy/postgres (canonical schema source)
- DISCORD_TOKEN
- dist/HotkeyTTS.exe
- docker-compose.postgres.yml
- Dockerfile
- ADR Index
- Clean Architecture / SOLID Principles
- DesktopAppConfig Dataclass
- Architecture Diagrams Guide
- Generated Architecture Diagrams Entry
- pyreverse Diagram Curation Workflow
- Architecture Transitions Guide
- GET /health Endpoint
- POST /speak Endpoint
- test_bot_desktop_http_contract.py
- GET /voice-context Endpoint
- Config (bot runtime)
- Container (composition root)
- DiscordCommands
- HTTPServer (bot)
- Note: important architectural handoff is presentation into shared use cases
- SpeakController
- SpeakTextUseCase
- TTSQueueOrchestrator
- VoiceContextController
- DesktopAppLifecycleCoordinator
- DesktopAppTTSProcessor
- DesktopAppTTSService
- DesktopAppUIRuntimeCoordinator
- DesktopMain
- DesktopTTSExecutionPort
- HotkeyManager
- HttpDiscordBotClient
- Note: DesktopAppUIRuntimeCoordinator owns queued UI actions and main-window lifecycle
- SpeakTextExecutionUseCase
- SystemTrayService
- DesktopTTSExecutionPort (generated)
- JoinVoiceChannelResult
- LeaveVoiceChannelResult
- ResultBase
- SpeakTextResult
- TTSConfigurationData
- TTSFallbackChain
- VoiceContextResult
- AudioFile
- AudioQueueItem
- IAudioFileCleanup
- IAudioQueue
- IConfigRepository
- ITTSEngine
- IVoiceChannel
- IVoiceChannelRepository
- TTSConfig
- TTSRequest
- ConsoleConfig
- DesktopAppConfig
- GUIConfig
- LocalPyTTSX3Engine
- NotificationService
- StandardKeyboardMonitor
- TTSEngine (desktop interface)
- DiscordVoiceChannelRepository
- EdgeTTSEngine
- GTTSEngine
- GuildConfigRepository
- InMemoryAudioQueue
- JSONConfigStorage
- Pyttsx3Engine
- RoutedTTSEngine
- TTSEngineFactory
- DiscordSpeakPresenter
- HTTPSpeakPresenter
- Note: core owns shared entities and contracts
- Note: desktop is runtime-specific and should reuse shared logic rather than duplicating it
- Maintenance rule: pyreverse output is discovery input, not final documentation
- Note: SpeakTextUseCase is the main shared bot TTS entrypoint
- Note: TTSQueueOrchestrator owns queued playback orchestration
- Explicit Contracts Guide (DTO vs Protocol vs dict)
- Discord Bot Entry Path
- Desktop App Entry Path
- Desktop Hotkey-to-Speech Flow
- DesktopAppTTSService
- DesktopAppHotkeyHandler
- DiscordCommands
- Runtime Flows Guide
- SpeakTextExecutionUseCase
- SpeakTextUseCase
- Smells That Say Keep This Runtime-Specific
- Smells That Say Move This To Shared
- docs/deploy/BACKUP_AND_RESTORE_DATABASE.md
- Interface language resolution order: user guild pref, Discord user locale, guild pref, Discord guild locale, en-US default
- Voice settings resolution order: user override, guild default, global default
- docs/deploy/DEPLOYMENT_GUIDE.md
- Scope note: deployment guidance is for Discord bot runtime only, not Desktop App
- OpenTofu as default IaC tool, Kubernetes optional (k3s/Minikube)
- docs/deploy/STAGING_AND_ROLLBACK.md
- Release GitHub Actions workflow (publishes GHCR tags, signs image, attaches provenance)
- Rollback Bot Image GitHub Actions workflow
- Note: WinSW does not auto-update code; requires explicit deploy step (manual, scheduled, or CI/CD)
- Channel discovery priority: connected channel, user ID lookup, error
- docs/desktop/DESKTOP_APP_GUIDE.md
- FFmpeg (Discord voice flow)
- Full Local Production Stack
- Local Bot Storage (JSON vs Postgres)
- docs/getting-started/SETUP.md
- Optional Redis Queue For The Bot
- uv (lockfile dependency sync)
- .venv Virtual Environment
- Testing Guide
- docs/getting-started/TESTING.md
- scripts/test/quality_gates.py
- CodeQL Scanning
- CycloneDX SBOM Tooling
- Dependabot
- pip-audit
- GET /health Endpoint
- GET /observability Endpoint
- Queue Critical Domain Coverage Gate (>=80%)
- Runtime Observability Critical Domain Coverage Gate (>=95%)
- SLI/SLO Baseline
- Chaos Testing Guide
- GET /ready Endpoint
- Disaster Recovery Drills Guide
- Chosen Upgrade Stack Decision
- Load Testing Guide
- Queue Load Baseline Non-Blocking Rationale
- Mutation CI Limitation (src.* import path incompatibility)
- Mutation Testing Guide
- Security Gates Guide
- Trivy Critical Vulnerability Blocking Gate
- Documentation Index
- docs/security/THREAT_MODEL.md
- .env.example
- .env.prod.example
- GitHub Container Registry (GHCR)
- Infrastructure GitHub Actions Workflow
- Release GitHub Actions Workflow
- GitHub Build Provenance Attestation
- Clean Architecture (project structure)
- Dependency Rule (Presentation -> Application -> Domain <- Infrastructure)
- ITTSEngine (example interface)
- SOLID Principles
- SpeakController (anti-pattern example: business logic in Presentation)
- SpeakTextUseCase (anti-pattern example: importing Infrastructure into Application)
- TTSRequest (anti-pattern example: Domain coupled to discord.Client)
- Non-negotiable Repository Rules
- Senior/Staff Decision Standard
- codacy_cli_analyze mandatory post-edit rule
- .github/workflows/deploy-bot-windows.yml
- GitOps Promotion via Git overlay newTag change
- Grafana
- HotkeyTTS.exe (Desktop App executable)
- infra/environments/dev
- infra/environments/prod
- infra/environments/staging
- infra/modules/environment_contract
- Infrastructure README (infra/)
- k3s (lightweight Kubernetes)
- Kustomize Kubernetes Manifests
- Minikube (local validation)
- mutmut (mutation testing tool)
- OpenSSF Scorecard
- OpenTofu (IaC Tool)
- otel-collector service
- pg_dump
- pg_restore
- Postgres Config (asset)
- Postgres (config storage)
- Prometheus
- PyInstaller
- pyreverse (diagram generation tool)
- QUEUE_GUILD_LOCK_TTL_SECONDS
- QUEUE_PROCESSING_LEASE_TTL_SECONDS
- Discord Bot (runtime app)
- Observability Stack (OpenTelemetry, Prometheus, Grafana)
- Persistence (JSON local / Postgres production)
- Queue Layer (in-memory / Redis-backed)
- Windows Desktop App (runtime app)
- REDIS_KEY_PREFIX (tts)
- Redis Queue (asset)
- Redis (queue backend)
- scripts/dev.ps1
- Scripts Directory README
- scripts/test/manual_integration_check.py
- scripts/test/manual_security_check.py
- scripts/test/test_discord_connection.py
- scripts/utils/backup_postgres.ps1
- scripts/utils/dependency_maintenance.py
- scripts/utils/migrate_json_config_to_postgres.py
- scripts/utils/restore_postgres.ps1
- /speak Endpoint
- .specify/ (canonical repository rules)
- .specify/memory/constitution.md (binding governance source)
- .specify/review-checklist.md
- src/application/desktop_tts.py
- src.application layer
- src/application/rate_limiting.py
- src/application/runtime_telemetry.py
- src/application/tts_queue_orchestrator.py
- src/application/tts_text.py
- src.bot_runtime layer (composition root)
- src/bot_runtime/queue_worker.py
- src/bot_runtime/settings.py
- src/core/
- src.core layer
- src/desktop/app/bootstrap.py (composition root)
- src/desktop/config/desktop_config.py
- src/desktop/config/models.py
- src/desktop/config/repository.py
- src.desktop layer
- src/desktop/services/discord_bot_client.py
- src/infrastructure/audio_queue.py
- src/infrastructure/http/server.py
- src.infrastructure layer
- src/infrastructure/runtime_observability.py
- src.presentation layer
- Tempo
- tests/chaos/test_dependency_failure_modes.py
- tests/load/test_queue_load_baseline.py
- Trivy (Docker image vulnerability scanner)
- uv.lock
- WinSW (Windows service wrapper)

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
- `assets/icon.png (project microphone icon)` --conceptually_related_to--> `Distributed TTS System`  [INFERRED]
  assets/icon.png → README.md
- `config/quality_gates.json` --semantically_similar_to--> `Codacy Coverage Threshold (77%)`  [INFERRED] [semantically similar]
  .github/workflows/test.yml → .codacy.yml
- `Production Postgres Service` --semantically_similar_to--> `Postgres-only Compose Service`  [INFERRED] [semantically similar]
  docker-compose.prod.yml → docker-compose.postgres.yml
- `Production Redis Service` --semantically_similar_to--> `Redis-only Compose Service`  [INFERRED] [semantically similar]
  docker-compose.prod.yml → docker-compose.redis.yml
- `SecurityTestChannel` --uses--> `VoiceChannelResolutionService`  [INFERRED]
  scripts/test/manual_security_check.py → src/application/voice_channel_resolution.py

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

## Communities (465 total, 303 thin omitted)

### Community 0 - "Desktop App Configuration"
Cohesion: 0.04
Nodes (55): DesktopBotVoiceContextStatus, DesktopApp, Start all runtime services., Run the main Desktop App loop., Execute queued UI actions on the main thread., Show the main Desktop App panel when Tkinter is available., Log the current Desktop App configuration summary., Update dependent services after configuration changes. (+47 more)

### Community 1 - "TTS Queue Orchestrator & Security"
Cohesion: 0.08
Nodes (32): Test the valid scenario where the user is in the bot channel., Test channel with a stable channel id., Test repository for security scenarios., Test the vulnerable scenario where the user moved channels., SecurityTestChannel, SecurityTestRepository, test_security_valid_scenario(), test_security_vulnerability() (+24 more)

### Community 2 - "TTS Execution Service"
Cohesion: 0.11
Nodes (27): Execute Desktop App TTS through an explicit Desktop App port., Return whether the underlying TTS service is available., SpeakTextExecutionUseCase, DesktopAppTTSService, DiscordTTSService, TTS service that sends text to the Discord bot., Main Desktop App TTS service that coordinates available engines., Speak the given text using available engines. (+19 more)

### Community 3 - "Core Interfaces & Telemetry"
Cohesion: 0.04
Nodes (54): Input DTO for speak-text use-case boundaries., Speak-text application use case., BotRuntimeTelemetry, NoOpBotRuntimeTelemetry, Protocol, Application-facing runtime telemetry contracts., Application-facing contract for bot runtime observability., Safe default telemetry implementation for tests and opt-out runtimes. (+46 more)

### Community 4 - "Redis Audio Queue"
Cohesion: 0.05
Nodes (30): AudioQueueItemStatus, Status of an audio queue item., _item_to_payload(), _normalize_guild_id(), _null_span_context, Any, Redis-backed FIFO queue with item metadata per guild., RedisAudioQueue (+22 more)

### Community 5 - "Bot Queue Worker"
Cohesion: 0.04
Nodes (30): Record the outcome of queued playback processing., AudioQueueItem, Represents an item in the audio queue.      Tracks a TTS request through the pro, Mark item as currently being processed., Mark item as successfully completed., Mark item as failed with error message.          Args:             error: Error, Get duration in seconds if completed., Get time waited in queue before processing. (+22 more)

### Community 6 - "Desktop Main Window GUI"
Cohesion: 0.16
Nodes (3): DesktopAppMainWindow, Any, Main Desktop App window that keeps configuration, actions, and logs visible.

### Community 7 - "Desktop Hotkey Backend"
Cohesion: 0.05
Nodes (47): Main entry point for the Windows desktop app., DesktopTTSServiceStatusDTO, Runtime status exposed by the Desktop App TTS processor., is_keyboard_backend_available(), KeyboardHookBackend, Adapter around the optional keyboard library., Return whether the keyboard backend is installed., Register a keyboard event callback. (+39 more)

### Community 8 - "TTS Audio Engines"
Cohesion: 0.06
Nodes (43): AudioFile, Represents an audio file path., Delete or release generated audio resources., Play audio in the voice channel.          Args:             audio: AudioFile to, FileAudioCleanup, Infrastructure helpers for cleaning up generated audio files., Delete temporary audio files from disk., EdgeTTSEngine (+35 more)

### Community 9 - "Bot Settings & Runtime Config"
Cohesion: 0.12
Nodes (27): Config, Validate required configuration.          Returns:             Tuple of (is_vali, Application configuration.      Follows Single Responsibility: only handles conf, Tests for bot runtime timeout configuration., test_config_accepts_postgres_backend_when_database_url_is_present(), test_config_allows_zero_rate_limit_window_when_limit_is_disabled(), test_config_exports_dotenv_values_for_process_runtime_checks(), test_config_reads_debug_log_level_override() (+19 more)

### Community 10 - "Config Migration to Postgres"
Cohesion: 0.05
Nodes (41): main(), migrate(), Migrate guild config files from JSON storage into Postgres., Dependency injection container., GuildConfigRepository, IConfigStorage, JSONConfigStorage, ABC (+33 more)

### Community 11 - "Desktop TTS Status Gateway"
Cohesion: 0.10
Nodes (17): DesktopTTSStatusGateway, DesktopTTSStatusUseCase, Build Desktop App status information for local/remote TTS availability., Return the typed TTS status for Desktop App runtime views., Port for status data needed by Desktop App TTS views., Return whether the remote/Discord path is available., Return whether local TTS is enabled in configuration., Return whether the local TTS adapter is usable. (+9 more)

### Community 12 - "Interface Language Preferences"
Cohesion: 0.07
Nodes (14): JSONInterfaceLanguagePreferenceRepository, PostgreSQLInterfaceLanguagePreferenceRepository, Any, Path, Persistence adapters for Discord interface language preferences., Store interface language preferences in Postgres with negative caching., Store interface language preferences in JSON files with negative caching., FailingConnection (+6 more)

### Community 13 - "Hotkey Monitoring Service"
Cohesion: 0.04
Nodes (36): HotkeyManagerStatusDTO, High-level hotkey manager status., HotkeyHandler, HotkeyService, KeyboardMonitor, ABC, Protocol, Check if currently monitoring. (+28 more)

### Community 14 - "Desktop Bot Gateway"
Cohesion: 0.04
Nodes (48): DesktopBotConnectionStatus, LogRecord, CheckDesktopBotConnectionUseCase, DesktopBotGateway, FetchDesktopBotVoiceContextUseCase, Protocol, Application use cases for Desktop App interactions with the bot runtime., Query the current detected voice context for the configured member. (+40 more)

### Community 15 - "Desktop Discord Bot Client"
Cohesion: 0.16
Nodes (10): BotErrorResponseDTO, BotHealthResponseDTO, Wire contract for GET /health responses., Normalized bot HTTP error payload., DiscordBotHttpResponse, DiscordBotHttpTransport, Return the bot voice-context endpoint URL., Fetch the current guild/channel detected for the configured member. (+2 more)

### Community 16 - "Deploy: K8s Observability Metrics"
Cohesion: 0.07
Nodes (42): bot_queue_age_seconds metric, bot_queue_depth metric, bot_queue_lock_loss_total metric (Redis-backed queue worker), bot_tts_enqueue_to_playback_seconds metric, bot_tts_submissions_total metric, bot-config ConfigMap, bot Deployment, bot-secrets Kubernetes Secret (external) (+34 more)

### Community 17 - "Discord Voice Channel & FFmpeg"
Cohesion: 0.15
Nodes (8): DiscordVoiceChannel, Play audio in the voice channel with resilient connection handling.          Arg, Discord voice channel wrapper.      Follows Single Responsibility: only handles, Get the channel name., Schedule automatic disconnect after idle timeout., Cancel scheduled disconnect., Initialize with discord.VoiceChannel.          Args:             channel: Discor, Check if member is still in the cached channel.

### Community 18 - "Architecture Diagrams: Runtime"
Cohesion: 0.27
Nodes (12): DiagramTarget, main(), Path, _pyreverse_args(), Generate architecture Mermaid diagrams from pyreverse output.  This script keeps, Generate Markdown-wrapped Mermaid diagrams and an index page., Describe one diagram generation target., Build the pyreverse argument list for one diagram target. (+4 more)

### Community 19 - "Desktop App Lifecycle"
Cohesion: 0.08
Nodes (30): ConfigT, Event, NotificationT, ProcessorT, DesktopAppLifecycleCoordinator, DesktopTTSProcessorLike, HotkeyManagerLike, NotificationServiceLike (+22 more)

### Community 20 - "Voice Channel Resolution"
Cohesion: 0.08
Nodes (16): Record the outcome of a speak request submission., Resolve a safe voice channel for a TTS request., VoiceChannelResolutionService, Represents a text-to-speech request., TTSRequest, mock_voice_channel(), MockVoiceChannel, Fixture for mock voice channel. (+8 more)

### Community 21 - "Discord Presenters & Results"
Cohesion: 0.12
Nodes (21): CommandTree, JoinVoiceChannelResult, LeaveVoiceChannelResult, Typed application result objects for shared TTS flows., Typed result base for shared application flows., ResultBase, RateLimitResult, Typed result for rate limit decisions. (+13 more)

### Community 22 - "Core Entities & Config"
Cohesion: 0.05
Nodes (23): TTS engine configuration., TTSConfig, Get resolved TTS configuration for a guild/user scope or the global default., Load resolved TTS configuration asynchronously for a guild/user scope or the glo, Set TTS configuration for a specific guild or guild/user scope., Persist TTS configuration asynchronously for a specific guild or guild/user scop, Generate audio file from text.          Args:             text: Text to convert, PostgreSQLConfigStorage (+15 more)

### Community 23 - "Discord Voice Channel Interfaces"
Cohesion: 0.09
Nodes (12): IVoiceChannel, Interface for voice channel operations., Connect to the voice channel., Disconnect from the voice channel., Check if connected to voice channel., Get the channel name., Get the guild ID for the voice channel., Get the guild name for the voice channel. (+4 more)

### Community 24 - "Discord Commands Tests"
Cohesion: 0.07
Nodes (6): Test /config command to get current config., Test /join when user is not in voice channel., Test /join when PyNaCl is missing., Test DiscordCommands presentation layer., Test /join delegates success handling to the use case., TestDiscordCommands

### Community 25 - "Desktop HTTP Bot Client"
Cohesion: 0.17
Nodes (6): Check whether HTTP requests can be sent to the bot., Build a speak request from Desktop App configuration., Build and send a text payload through the bot runtime., Return the bot speak endpoint URL., Send a speak request to the configured Discord bot., Build a user-facing error message from an HTTP failure.

### Community 26 - "Discord i18n & Locale"
Cohesion: 0.07
Nodes (29): Locale, locale_str, Protocol, Application contracts for Discord voice runtime availability., Port for checking whether Discord voice runtime support is available., Return the current runtime availability details., VoiceRuntimeAvailability, Discord bot commands. (+21 more)

### Community 27 - "Desktop GUI Logging"
Cohesion: 0.24
Nodes (7): build_action_buttons(), build_header(), build_help_section(), Layout helpers for Desktop App main window sections., Build the main action row., Build the usage help section., Build the main window title and introductory copy.

### Community 28 - "Pyttsx3 TTS Adapter"
Cohesion: 0.07
Nodes (29): Future, Logger, Pyttsx3Adapter, Thin adapter around pyttsx3 initialization., Return whether pyttsx3 is installed., Create a pyttsx3 engine instance., Create and configure a pyttsx3 engine instance., _cleanup_temp_audio_file_when_done() (+21 more)

### Community 29 - "Desktop Config Dialogs"
Cohesion: 0.20
Nodes (15): build_fake_tk_module(), build_fake_ttk_module(), DummyVar, test_console_config_keeps_existing_values_when_inputs_are_blank(), test_gui_config_create_tabs_populates_variables(), test_gui_config_handle_voice_selection_updates_fields(), test_gui_config_save_config_saves_valid_configuration(), test_gui_config_save_config_shows_validation_errors() (+7 more)

### Community 30 - "Speak HTTP Controller"
Cohesion: 0.12
Nodes (22): SpeakTextResult, Use case for accepting TTS requests and delegating queued playback., SpeakTextUseCase, Controller for /speak endpoint., SpeakController, _speak_request(), test_rate_limit_retry_without_retry_after_keeps_contract_message(), test_speak_contract_accepts_authenticated_json_request() (+14 more)

### Community 31 - "Deploy Docs: Observability & Rollback"
Cohesion: 0.20
Nodes (4): Argo CD GitOps, Current Baseline, Load Testing, Local Run

### Community 32 - "TTS Voice Catalog GUI"
Cohesion: 0.07
Nodes (28): Shared execution services for TTS flows., Structured result for Desktop App TTS execution., TTSExecutionResult, Wire tray callbacks and hotkey processing to the current services., Wire tray callbacks to the provided notification service., Recreate the hotkey manager so it points at the latest services., Initialize all Desktop App components., DesktopAppHotkeyHandler (+20 more)

### Community 33 - "Speak Use Case Tests"
Cohesion: 0.11
Nodes (13): build_speak_use_case(), Factory for SpeakTextUseCase with explicit collaborators., Speak use case should reuse the shared TTS text preparation rules., Speak use case should derive the guild from the member's current voice channel., Test that use case finds channel by channel_id first., Queue overflow should reject the request instead of faking a queued success., Test SpeakTextUseCase., Test successful execution of speak use case. (+5 more)

### Community 34 - "Discord Command Config"
Cohesion: 0.17
Nodes (5): Choice, DiscordSpeakPreparationErrorCode, DiscordCommands, Interaction, Discord slash commands handler.

### Community 35 - "Config Embed Builder"
Cohesion: 0.16
Nodes (15): Embed, ConfigureTTSResult, Structured availability details for Discord voice support., Return whether all required runtime dependencies are present., Return the names of missing runtime dependencies., VoiceRuntimeStatus, _BaseConfigEmbedBuilder, DiscordAboutCommandHandler (+7 more)

### Community 36 - "Quality Gates & Coverage"
Cohesion: 0.09
Nodes (22): Building Evolutionary Architectures, Clean Architecture, Clean Code, Concepts The Repository Intentionally Applies, Concepts To Apply Carefully, Core References And Their Practical Impact, Design Patterns: Elements of Reusable Object-Oriented Software (GoF), Designing Data-Intensive Applications (+14 more)

### Community 37 - "Voice Channel Use Cases"
Cohesion: 0.12
Nodes (8): JoinVoiceChannelUseCase, LeaveVoiceChannelUseCase, Use case for connecting the bot to a member's current voice channel., Use case for disconnecting the bot from a guild voice channel., Join use case should connect to the member channel., Leave use case should disconnect an active guild voice channel., Leave use case should report not connected when no voice session exists., Create a DiscordCommands instance for testing.

### Community 38 - "Dependency Maintenance Script"
Cohesion: 0.09
Nodes (52): Namespace, ParseResult, _build_parser(), _class_matches_path(), _coverage_line_totals(), CoverageDomainGate, CoverageGateConfig, CoverageGateResult (+44 more)

### Community 39 - "Configure TTS Use Case"
Cohesion: 0.09
Nodes (14): TTSConfigurationData, ConfigureTTSUseCase, TTS configuration application use case., Use case for configuring TTS settings per guild., Public import surface for shared application use cases.  This module is intentio, Test ConfigureTTSUseCase., Test getting current configuration., Test updating TTS engine. (+6 more)

### Community 40 - "Interface Language Discord Commands"
Cohesion: 0.16
Nodes (3): ConfigureInterfaceLanguageUseCase, Configure interface language preferences without changing TTS voice settings., FakeInterfaceLanguagePreferenceRepository

### Community 41 - "Bot Runtime Container"
Cohesion: 0.14
Nodes (13): Container, Sync slash commands only once per process to avoid reconnect churn., Centralize dependency construction and wiring., _build_config(), test_container_requires_redis_dependency_for_redis_backend(), test_container_uses_inmemory_audio_queue_by_default(), test_container_uses_json_storage_when_configured(), test_container_uses_postgres_storage_when_configured() (+5 more)

### Community 42 - "Docs: Dependency & Elite Upgrade Plan"
Cohesion: 0.33
Nodes (5): Artifact Verification, Automated Gates, Release Expectations, Runtime Entry Points, Security Gates

### Community 43 - "Desktop Config Dialog Helpers"
Cohesion: 0.13
Nodes (22): Presentation helpers for Desktop App configuration dialogs., build_updated_config(), normalize_optional_text(), prompt_numeric_input(), Return stripped text or None when blank., Return stripped text or fallback when blank., Prompt until the user provides a numeric value or keeps the current one., Validate a numeric text field and return an error message when invalid. (+14 more)

### Community 44 - "In-Memory Config Repository"
Cohesion: 0.10
Nodes (14): InMemoryConfigRepository, Initialize repository with default configuration.          Args:             def, Get resolved TTS configuration for a guild/user scope or the global default., Load configuration asynchronously using the in-memory state., Set TTS configuration for a specific guild or guild/user scope.          Args:, Persist configuration asynchronously using the in-memory state., In-memory configuration storage.      Follows Single Responsibility: only manage, Test getting default configuration. (+6 more)

### Community 45 - "Fake Redis Audio Queue Tests"
Cohesion: 0.12
Nodes (15): _configure_logging(), main(), Main entry point for Discord bot with HTTP server.  This is the refactored versi, run(), Tests for bot entry point., Test that bot has async main function., Test noisy library loggers are reduced at INFO without hiding errors., Test bot.py entry point. (+7 more)

### Community 46 - "Docs: Release & Runbooks"
Cohesion: 0.08
Nodes (24): Alertmanager Incident Routing, Contain, Contain, Contain, Engine Degradation, First Response, Follow-Up, Follow-Up (+16 more)

### Community 48 - "TTS Voice Catalog Runtime"
Cohesion: 0.09
Nodes (20): Application contracts for exposing user-selectable TTS voice options., A selectable voice option exposed to presentation layers., TTSVoiceOption, ConfigInterface, ABC, Shared contracts for Desktop App configuration dialogs., Abstract interface for Desktop App configuration flows., Show a configuration UI and return the updated config when accepted. (+12 more)

### Community 49 - "Postgres Config Storage"
Cohesion: 0.10
Nodes (13): LocalPyTTSX3Engine, ABC, Return the latest local TTS error, when any., Create the shared Desktop App TTS flow service., Abstract base class for TTS engines., Speak the given text. Returns True if successful., Check if the TTS engine is available., Return the last human-readable error for the engine. (+5 more)

### Community 50 - "Desktop Config Validation"
Cohesion: 0.05
Nodes (41): Shared timeout defaults used across bot and desktop runtimes., Return whether the Desktop App has minimum required configuration., Validate the provided Desktop App configuration., EnvironmentUpdater, Updates environment variables from configuration., DesktopAppConfig, DiscordConfig, get_default_bot_speak_token() (+33 more)

### Community 51 - "Initial Setup Dialog"
Cohesion: 0.26
Nodes (6): InitialSetupResult, Structured output for the initial Desktop App setup flow., InitialSetupGUI, Initial setup GUI for first-time configuration., test_console_initial_setup_handles_invalid_ids_and_defaults(), test_initial_setup_gui_skip_discord_sets_result_and_destroys_root()

### Community 52 - "Voice Runtime Status"
Cohesion: 0.15
Nodes (15): has_ffmpeg_runtime(), _is_usable_executable(), FFmpeg runtime helpers for Discord voice support., Return whether the given path points to an executable file., Return the FFmpeg executable path from env or PATH., Return whether FFmpeg is available for the current process., resolve_ffmpeg_executable(), Discord voice channel implementation. (+7 more)

### Community 53 - "Infrastructure HTTP Server"
Cohesion: 0.16
Nodes (15): HTTPServer, Application, HTTP server for bot endpoints.      Follows Single Responsibility: only handles, Build aiohttp application with operational and integration endpoints., test_bot_health_endpoint_smoke(), Tests for aiohttp HTTP server endpoints., test_http_server_applies_cors_headers_for_allowed_origin(), test_http_server_configures_max_request_body_size() (+7 more)

### Community 54 - "Discord.py Dependency Docs"
Cohesion: 0.06
Nodes (38): Bot /health and /ready endpoints, Cosign keyless image signing, discord.py, docker-compose.prod.yml, Dockerfile (bot image build), pyright (typecheck), ruff (lint), Dependency Maintenance Guide (+30 more)

### Community 55 - "Rate Limiting"
Cohesion: 0.18
Nodes (15): Protocol, RateLimiter, RateLimitRequest, Shared rate limiting contracts for runtime entrypoints., Input used by runtimes to check a caller-specific rate limit., Contract implemented by runtime-specific rate limit adapters., InMemoryRateLimiter, In-memory rate limiting adapter for runtime entrypoints. (+7 more)

### Community 56 - "Runtime Telemetry Spans"
Cohesion: 0.09
Nodes (9): AbstractContextManager, NullRuntimeSpan, NullRuntimeSpanContext, Any, BaseException, Protocol, Shared observability contracts for application and presentation layers., RuntimeSpan (+1 more)

### Community 57 - "Voice Context Query DTOs"
Cohesion: 0.13
Nodes (12): BotVoiceContextResponseDTO, Wire contract for GET /voice-context responses., VoiceContextResult, HTTPSpeakPresenter, HTTPVoiceContextPresenter, HTTP-specific presentation mapping for typed application results., Map speak results to HTTP text and status., Map voice-context results to HTTP JSON/status. (+4 more)

### Community 58 - "TTS Fallback Routing"
Cohesion: 0.08
Nodes (24): Logger, Protocol, Shared Desktop App TTS orchestration helpers., Port for a synchronous TTS engine used by the Desktop App., Return whether the engine can be used., TTSEnginePort, build_tts_engine_chain(), Logger (+16 more)

### Community 59 - "System Tray Notifications"
Cohesion: 0.11
Nodes (9): Any, PySystemTrayIcon, Show system tray icon., Hide system tray icon., pystray adapter is available when constructed., Return whether the tray event loop is running., pystray-backed system tray adapter., Set callback handlers for tray actions. (+1 more)

### Community 60 - "Desktop Settings Dialog"
Cohesion: 0.19
Nodes (3): GUIConfig, Any, GUI configuration interface.

### Community 61 - "Hotkey Text Capture"
Cohesion: 0.13
Nodes (10): HotkeyCaptureResult, HotkeyTextCaptureSession, Pure hotkey text-capture state used by the Desktop App keyboard monitor., Structured result produced when a capture session is completed., Track buffered text between configured trigger keys., Clear current recording state., Consume a key press and return a completed capture when available., test_hotkey_capture_session_ignores_empty_capture_and_reset_clears_state() (+2 more)

### Community 62 - "TTS Execution Port"
Cohesion: 0.15
Nodes (8): DesktopTTSExecutionPort, Protocol, Port for Desktop App TTS execution and status reporting., Execute speech for the provided normalized text., Return whether the underlying TTS flow is available., Return runtime status details for the Desktop App., Return the latest execution error when available., Execute a text-to-speech request and return a neutral result payload.

### Community 63 - "Bot Readiness Probes"
Cohesion: 0.14
Nodes (16): AudioQueueHealthPort, BotReadinessConfig, ConfigRepositoryHealthPort, ConfigStorageHealthPort, DiscordClientReadinessPort, Protocol, QueueWorkerReadinessPort, Readiness checks for the Discord bot runtime. (+8 more)

### Community 64 - "Desktop App TTS Service"
Cohesion: 0.08
Nodes (11): is_pyttsx3_available(), Expose pyttsx3 availability for status reporting., _DesktopAppTTSStatusGateway, Check if pyttsx3 is available., Check if Discord TTS is available., Check if TTS service is available., Return whether the Discord bot transport is currently usable., Return whether the configured local engine is available. (+3 more)

### Community 65 - "Mock Audio Queue Tests"
Cohesion: 0.09
Nodes (10): AudioQueueStatusDTO, Queue details for a guild-scoped audio queue., mock_audio_queue(), MockAudioQueue, Mock audio queue for testing., Remove and return next item., Persist in-memory item updates for tests., Renew a mock guild lock. (+2 more)

### Community 66 - "Core Entities Tests"
Cohesion: 0.07
Nodes (18): Tests for core entities., Test creating TTSRequest with all fields., Test AudioFile string representation., Test creating TTSRequest with only text., Test TTSRequest equality comparison., Test TTSRequest string representation., Test TTSConfig entity., Test default TTSConfig values. (+10 more)

### Community 67 - "OpenTelemetry Fake Exporters"
Cohesion: 0.14
Nodes (14): _FakeCounter, _FakeMetricExporter, _FakeMetricReader, _FakePropagate, _FakeResource, _FakeSpanExporter, _FakeSpanKind, _FakeSpanProcessor (+6 more)

### Community 68 - "System Tray Notification Service"
Cohesion: 0.13
Nodes (17): System tray availability and runtime status., SystemTrayStatusDTO, Start system tray service only after startup is confirmed., Run system tray (blocking call)., Check if system tray support exists in the environment., Check if the tray loop is actually running., Get system tray service status., Service for managing system tray functionality. (+9 more)

### Community 69 - "Voice Context Controller"
Cohesion: 0.13
Nodes (12): Normalized input contract for current voice-context queries., VoiceContextQueryDTO, GetCurrentVoiceContextUseCase, Voice-channel related application use cases., Use case for discovering the member's current voice context., HTTP controllers for handling web requests., Controller for querying the current voice context for a member., VoiceContextController (+4 more)

### Community 70 - "Generated Diagrams: Config Repository"
Cohesion: 0.29
Nodes (7): Bot Production Persistence, Initial schema, Next recommended evolution, Recommendation, Runtime configuration, Suggested rollout, Why Postgres

### Community 71 - "Desktop TTS Bot Client"
Cohesion: 0.12
Nodes (11): AudioDevice, DesktopTTSBotClient, Protocol, Send text to the Discord bot for TTS., Protocol for audio device selection., Set the output device for audio playback., Minimal bot-client behavior needed by Desktop App TTS delivery., Return whether the bot client can send requests. (+3 more)

### Community 73 - "Codacy CI Workflow"
Cohesion: 0.15
Nodes (13): CODACY_PROJECT_TOKEN secret, Bandit Engine, Codacy Coverage Threshold (77%), Prospector Engine, Pylint Engine, config/quality_gates.json, Test Workflow, Test: critical-tests job (+5 more)

### Community 74 - "HTTP Speak Presenter"
Cohesion: 0.21
Nodes (14): build_main_window(), DummyLabel, DummyRoot, DummyVar, test_main_window_clear_logs_resets_widget_and_pushes_log(), test_main_window_drain_logs_appends_messages_and_reschedules(), test_main_window_drain_ui_actions_runs_callback_and_reschedules(), test_main_window_handle_refresh_voice_context_updates_voice_context_message() (+6 more)

### Community 75 - "Docs: Copilot & Architecture Guide"
Cohesion: 0.10
Nodes (20): app.py (desktop app entrypoint), deploy/winsw/install-or-update-service.ps1, dist/HotkeyTTS.exe, docs/architecture/ARCHITECTURE.md, docs/README.md, Documentation placement, GitHub Copilot Instructions, Non-negotiable rules (+12 more)

### Community 76 - "Discord Speak Request Builder"
Cohesion: 0.09
Nodes (18): DiscordSpeakPreparationResult, DiscordSpeakRequestBuilder, Protocol, Application service for preparing Discord speak-command input., Prepared speak input or a user-facing validation error., Minimal config lookup needed to build a speak request., Return the effective TTS config for a guild/user., Build speak-command input from Discord interaction primitives. (+10 more)

### Community 77 - "Desktop UI Runtime Coordinator"
Cohesion: 0.23
Nodes (10): DesktopAppUIRuntimeCoordinator, Queue a UI action to run on the main thread., Run all queued UI actions without blocking the Tk main loop., Own Desktop App window state, queued UI actions, and tray-triggered UI flows., test_ui_runtime_coordinator_drains_queued_actions(), test_ui_runtime_coordinator_handle_configure_focuses_existing_window(), test_ui_runtime_coordinator_queues_actions(), test_ui_runtime_coordinator_show_status_focuses_existing_window() (+2 more)

### Community 78 - "Desktop App Build Docs"
Cohesion: 0.09
Nodes (19): Architecture Diagrams, Diagram set, Editing guidance, Generated Architecture Diagrams, When to use generated diagrams, How to keep them updated, Recommended reading order, Why these diagrams exist (+11 more)

### Community 79 - "Threat Model & Rate Limits"
Cohesion: 0.20
Nodes (9): Abuse Cases, Actors, Assets, Logging Rules, Open Follow-Ups, Runtime Controls, Runtime Threat Model, Scope (+1 more)

### Community 80 - "Desktop App Status Builder"
Cohesion: 0.18
Nodes (11): DesktopTTSProcessorStatusPort, HotkeyManagerStatusPort, NotificationServiceStatusPort, Protocol, Contract needed to determine Desktop App hotkey activity., Return whether hotkey monitoring is active., Contract needed to determine Desktop App TTS availability., Return the typed TTS runtime status. (+3 more)

### Community 81 - "Desktop Discord Bot Client Requests"
Cohesion: 0.11
Nodes (12): BotSpeakRequestDTO, Wire contract for POST /speak requests sent to the bot runtime., Serialize the request into the JSON payload expected by the bot., DiscordBotClient, Protocol, Port for sending TTS requests to the Discord bot runtime., Return whether the bot client is ready for requests., Build a speak request from the provided text. (+4 more)

### Community 82 - "HTTP Server Tracing"
Cohesion: 0.26
Nodes (5): Request, Response, Health check endpoint for container and runtime probes., Expose a compact runtime observability snapshot for operational baselines., Readiness endpoint that checks configured external dependencies.

### Community 83 - "Postgres Deploy & Restore Docs"
Cohesion: 0.40
Nodes (4): Chaos Testing, Current Scope, Future Runtime Drills, Local Run

### Community 84 - "Desktop UI Configuration Coordinator"
Cohesion: 0.21
Nodes (8): ConfigurationCoordinatorLike, HotkeyManagerLike, Protocol, Handle configure requests from tray or fallback UI flow., Contract needed for configure flows triggered from the tray., Return whether hotkeys are active., Contract for the tray-triggered configuration flow., Run the configuration flow and return the updated config.

### Community 85 - "Desktop Config Models"
Cohesion: 0.10
Nodes (21): 1. Download WinSW, 2.5. Prepare the server `.env`, 2. Copy the XML template, 3. Optional: run with a dedicated service account, 4. Install the service, Bot HTTP API is not reachable from another machine, Does it auto-update when `main` changes?, Install steps (+13 more)

### Community 86 - "Notification Service Protocol"
Cohesion: 0.15
Nodes (8): Protocol, Create appropriate system tray icon based on availability., Protocol for system tray functionality., Show the system tray icon., Set the tooltip text., Check if system tray is available., Check if the tray loop is running., SystemTrayIcon

### Community 87 - "OpenTelemetry Fake Spans"
Cohesion: 0.20
Nodes (3): _FakeSpan, _FakeStartedSpan, test_disabled_runtime_span_contexts_are_noops()

### Community 88 - "In-Memory Runtime Telemetry"
Cohesion: 0.13
Nodes (10): deque, BotRuntimeObservabilityDTO, Operational snapshot for baseline bot-runtime observability., Return the current operational snapshot., InMemoryBotRuntimeTelemetry, In-memory operational metrics for the Discord bot runtime., Track a compact rolling baseline of bot runtime metrics., test_bot_observability_sli_baseline_smoke() (+2 more)

### Community 89 - "ADR: Docker Compose Postgres"
Cohesion: 0.04
Nodes (37): ADR 0001: Record Architecture Decisions, Consequences, Context, Decision, Status, ADR 0002: Use Postgres For Production Bot Configuration, Consequences, Context (+29 more)

### Community 91 - "Bot Readiness DB Ports"
Cohesion: 0.18
Nodes (5): Self, DatabaseConnectionPort, DatabaseCursorPort, Minimal DB cursor surface used by readiness pings., Minimal DB connection/context-manager surface.

### Community 92 - "Desktop Config Paths"
Cohesion: 0.15
Nodes (4): BotQueueWorker, _null_span_context, Poll queue backends and drain pending guild queues., Refresh the distributed guild lock while processing is still active.          Ar

### Community 93 - "OpenTelemetry Audio Queue"
Cohesion: 0.14
Nodes (6): _NullSpan, OpenTelemetryRuntime, Any, BaseException, Optional OpenTelemetry tracing and metrics for the bot runtime., Provide tracing and metrics with a safe no-op fallback.

### Community 94 - "OpenTelemetry Fake Providers"
Cohesion: 0.18
Nodes (4): _FakeProvider, _FakeTracer, _FakeTracerProvider, test_shutdown_flushes_meter_and_tracer_providers()

### Community 95 - "Deploy: Tempo Tracing"
Cohesion: 0.08
Nodes (24): Tempo Local Trace Storage Backend, Tempo Metrics Generator, Tempo OTLP Receiver (http/grpc), Tempo Distributed Tracing Config, OpenTelemetry Collector Config, Metrics Pipeline (otlp -> prometheus), Collector OTLP Receiver (http/grpc), Prometheus Metrics Exporter (+16 more)

### Community 96 - "Clean Architecture Docs"
Cohesion: 0.13
Nodes (15): Config, Dependency Rules, Desktop App, Desktop App, Discord Bot, Entry Points, Execution, Main Structure (+7 more)

### Community 98 - "Desktop App Status DTOs"
Cohesion: 0.22
Nodes (7): DesktopAppRuntimeStatusDTO, Aggregated Desktop App runtime status for tray and UI consumers., Get a compact view of current runtime status., NotificationInfoPort, Show current app status via the main window or tray notifications., Contract needed to show tray status notifications., Show an informational notification.

### Community 99 - "Desktop Config Environment"
Cohesion: 0.08
Nodes (24): DesktopConfigEnvironment, DesktopConfigRepository, DesktopConfigurationApplicationService, Protocol, Application services for Desktop App configuration flows., Port for Desktop App configuration persistence., Persist the provided Desktop App configuration., Port for synchronizing Desktop App configuration into the environment. (+16 more)

### Community 100 - "Bot-Desktop HTTP Contract Tests"
Cohesion: 0.50
Nodes (4): Application, StreamResponse, _route(), test_health_and_readiness_contracts_are_json()

### Community 101 - "OpenTelemetry Fake Meters"
Cohesion: 0.20
Nodes (3): _FakeHistogram, _FakeMeter, _FakeMeterProvider

### Community 104 - "Manual Integration Check Script"
Cohesion: 0.25
Nodes (10): main(), Test the configured Discord bot endpoint when DISCORD_BOT_URL is set., Check whether required release files exist., Compile the desktop entry point without executing GUI code., Run all manual integration checks., Check whether required and optional runtime packages are installed., test_basic_functionality(), test_dependencies() (+2 more)

### Community 105 - "Desktop Notification Service"
Cohesion: 0.18
Nodes (7): NotificationService, ABC, Abstract interface for notification services., Show an informational notification., Show a success notification., Show an error notification., Check if notification service is available.

### Community 106 - "OpenTelemetry Null Span"
Cohesion: 0.11
Nodes (19): Disaster Recovery Drills, Drill Cadence, Environment Rollback, Image-Based Rollback, Non-Destructive Drill, Postgres Restore Drill, Preconditions, Preconditions (+11 more)

### Community 107 - "GitHub Contributing Guide"
Cohesion: 0.20
Nodes (9): Adding Features, Contributing To TTS Hotkey Windows, Dependency Rules, Project Architecture, Pull Request Checklist, Questions, Reporting Bugs, Resources (+1 more)

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
Cohesion: 0.40
Nodes (6): prod-application.yaml (ArgoCD Application), staging-application.yaml (ArgoCD Application), deploy/k8s/overlays/* (Kustomize overlays), Infrastructure (iac.yml) workflow, infra/environments/* (OpenTofu environments), OpenTofu Infrastructure as Code

### Community 114 - "HTTP Server Observability"
Cohesion: 0.29
Nodes (5): ObservabilitySnapshotProvider, ReadinessProvider, RequestHandler, StreamResponse, Initialize HTTP server.          Args:             speak_handler: Handler for /s

### Community 115 - "Bot Readiness Chaos & Failure"
Cohesion: 0.56
Nodes (8): BotReadinessProbe, Evaluate whether the bot runtime is ready to receive production traffic., _config(), _dependency(), test_readiness_reports_not_ready_when_postgres_connect_method_is_missing(), test_readiness_reports_not_ready_when_postgres_is_unavailable(), test_readiness_reports_not_ready_when_queue_worker_is_stopped(), test_readiness_reports_not_ready_when_redis_ping_raises()

### Community 116 - "Null System Tray Icon"
Cohesion: 0.20
Nodes (4): NullSystemTrayIcon, Null object used when no tray implementation is available., test_null_system_tray_icon_is_never_available(), test_system_tray_service_start_returns_false_when_unavailable()

### Community 117 - "System Tray Icon Adapter"
Cohesion: 0.22
Nodes (3): Abstractable base for system tray adapters., Set callback handlers for tray actions., SystemTrayIconAdapter

### Community 118 - "Assets: App Icon"
Cohesion: 0.12
Nodes (16): assets/icon.png (project microphone icon), Architecture, Author, Contents, Distributed TTS System, Documentation, Future Improvements, License (+8 more)

### Community 122 - "Edge-TTS Engine"
Cohesion: 0.16
Nodes (10): DesktopTTSFlowService, Speak the given text., Coordinate text preparation and engine fallback for Desktop App TTS., Prepare and speak text using the configured fallback chain., Return whether at least one configured TTS engine is available., Expose the latest error captured by the fallback chain., FakeEngine, test_desktop_tts_flow_service_ignores_blank_text() (+2 more)

### Community 123 - "Core Timeout Config"
Cohesion: 0.12
Nodes (11): DesktopTTSExecutionService, KeyboardCleanupPort, Protocol, Check if keyboard events are currently suppressed by cleanup., Contract used by the Desktop App TTS processor., Execute TTS for the given text., Return whether TTS is currently available., Return typed TTS status information. (+3 more)

### Community 124 - "Desktop Config Reconfigure Action"
Cohesion: 0.33
Nodes (4): NotificationFeedbackPort, Contract used to show configuration feedback., Show an error notification., Show a success notification.

### Community 125 - "Manual Discord Connection Test"
Cohesion: 0.38
Nodes (6): load_env_file(), main(), Load the first available .env file from common local locations., Send a request to the Discord bot the same way the Desktop App does., Run the manual Discord connection check., test_discord_request()

### Community 126 - "Desktop Config Validator"
Cohesion: 0.12
Nodes (17): Desktop App in `.venv`, Environment, Future Categories, Good Practices, Integration tests, Manual validation, Recommended Execution Flow, Running Integration Tests (+9 more)

### Community 127 - "Architecture Boundary Tests"
Cohesion: 0.52
Nodes (6): _find_forbidden_imports(), _iter_python_files(), _matches_forbidden_prefix(), test_application_layer_does_not_import_infrastructure(), test_clean_architecture_layers_keep_inward_dependency_flow(), test_presentation_layer_does_not_import_infrastructure()

### Community 128 - "OTel Collector Pipeline"
Cohesion: 0.20
Nodes (9): DesktopAppMainWindowPresenter, MainWindowMessage, Presentation helpers for the Desktop App main window., View-ready text and color for a main-window status field., Build user-facing messages for the Desktop App main window., test_main_window_presenter_builds_incomplete_config_message_with_local_fallback(), test_main_window_presenter_builds_invalid_value_message(), test_main_window_presenter_builds_ready_config_message() (+1 more)

### Community 130 - "Audio Queue Status Interface"
Cohesion: 0.33
Nodes (4): AudioQueueStatusView, Protocol, Core-facing view of queue status without depending on application DTOs., Get current queue status for a guild.          Args:             guild_id: Guild

### Community 133 - "Desktop Hotkey Config Model"
Cohesion: 0.12
Nodes (15): 1. Inspect the current state, 2. Choose the upgrade style, 3. Upgrade in the environment first, 4. Update the requirement files deliberately, 5. Validate the migration, Best Practices, Dependency Maintenance, Goals (+7 more)

### Community 134 - "Getting Started: Environment Setup"
Cohesion: 0.11
Nodes (18): 1. Create `.venv`, 2. Activate `.venv`, 3. Install Dependencies, 4. Install FFmpeg On Windows For Discord Voice, 5.1. Local Bot Storage, 5.2. Optional Redis Queue For The Bot, 5.3. Full Local Production Stack, 5. Validate The Environment (+10 more)

### Community 177 - "Scripts Directory"
Cohesion: 0.12
Nodes (16): Build Scripts, CI/CD Integration, Contributing, Dependency Errors, Included Capabilities, Linux Permissions, Manual Checks, PowerShell Not Found (+8 more)

### Community 178 - "__init__.py"
Cohesion: 0.17
Nodes (13): AudioQueueItemStatusDTO, BotReadinessResponseDTO, BotRuntimeErrorRateDTO, DiscordVoiceChannelCacheStatsDTO, HotkeyServiceStatusDTO, Explicit DTO contracts shared across application and desktop runtime flows., Wire contract for GET /ready responses., Error-rate breakdown for a single guild or engine bucket. (+5 more)

### Community 179 - ".is_connected"
Cohesion: 0.18
Nodes (8): Disconnect from the voice channel., Check if connected to voice channel., Auto-disconnect after timeout., Clean up voice channel instances that haven't been used recently.          Remov, Synchronize cached voice client with Discord's guild state., Clean up all cached voice channel instances.          Useful for graceful shutdo, Connect to the voice channel with retry logic., VoiceClient

### Community 180 - "DiscordVoiceChannelRepository"
Cohesion: 0.17
Nodes (9): DiscordVoiceChannelRepository, Repository for finding Discord voice channels.      Follows Single Responsibilit, Find any voice channel where bot is already connected.          VALIDATION: Retu, Find voice channel where member is connected.          VALIDATION: Ensures membe, Find voice channel by ID.          Args:             channel_id: Channel ID, Find first available voice channel in guild.          Args:             guild_id, Update member cache on voice state change.          Args:             member_id:, Get statistics about the channel instance cache.          Returns:             T (+1 more)

### Community 181 - "Runtime Flows"
Cohesion: 0.13
Nodes (14): Bot `/speak`, Design note, Desktop App flow, Desktop hotkey to speech, Discord bot flow, Entry path, Entry path, Main responsibilities (+6 more)

### Community 182 - "Release Checklist"
Cohesion: 0.13
Nodes (15): Bot, Closeout, Deploy, Desktop, Desktop App, Discord Bot, Immediate Post-Deploy Checks, Metrics Check (+7 more)

### Community 183 - "README.md"
Cohesion: 0.14
Nodes (8): Generated Application Diagram, Generated Core Diagram, Generated Desktop Runtime Diagram, Generated Infrastructure Diagram, Generated Presentation And Bot Runtime Diagram, Files, Generated Architecture Diagrams, Regeneration

### Community 184 - "Elite Upgrade Implementation Plan"
Cohesion: 0.14
Nodes (13): Chosen Upgrade Stack, Commit And Validation Rule, Current Baseline, Elite Upgrade Implementation Plan, Implementation Status, Non-Goals For The First Pass, Phase 1: Supply Chain Security, Phase 2: Release Engineering (+5 more)

### Community 185 - "InterfaceLanguagePreferenceRepository"
Cohesion: 0.15
Nodes (7): InterfaceLanguagePreferenceRepository, Protocol, Persistence contract for interface language preferences., Return a user's explicit interface language for a guild, if any., Return a guild's explicit default interface language, if any., Persist a user's explicit interface language for a guild., Persist a guild's explicit default interface language.

### Community 186 - "settings.py"
Cohesion: 0.21
Nodes (7): _clear_stale_dotenv_values(), _load_environment_snapshot(), Path, Configuration management using environment variables., Load dotenv values and return the effective environment snapshot., Initialize configuration.          Args:             env_file: Path to .env file, _read_dotenv_values()

### Community 187 - "Deployment Guide"
Cohesion: 0.17
Nodes (12): Deployment Guide, I need backup and restore for the database, I need production runbooks or release operations, I need staging or rollback guidance, I only need environment variables, I want Docker plus Postgres, I want only local Postgres, I want the simplest Windows Server deploy (+4 more)

### Community 188 - "interface_language_preferences.py"
Cohesion: 0.17
Nodes (5): InterfaceLanguagePreferenceResult, Use cases for Discord interface language preferences., Result for interface language preference updates., Delete a user's explicit interface language preference., Delete a guild's explicit default interface language.

### Community 190 - "Docker + Postgres + Redis Deploy"
Cohesion: 0.18
Nodes (11): 1. Prepare environment, 2.1. Local Postgres only, 2. Start the stack, 3. Check status, 3. Explore telemetry, 4. Stop the stack, Credential change note, Docker + Postgres + Redis Deploy (+3 more)

### Community 191 - "Project Rules"
Cohesion: 0.18
Nodes (10): Architecture boundary (hard rule), Contracts, Documentation placement, Environment, Language and encoding, Project Rules, Transition code, Two runtimes (+2 more)

### Community 192 - "queue_worker.py"
Cohesion: 0.20
Nodes (7): _default_lock_renew_interval_seconds(), Protocol, QueueOrchestratorPort, Background queue worker for Discord bot delivery., Minimal queue orchestrator behavior needed by the worker., Process the next item for a guild., Return a safe renew cadence for distributed locks and leases.

### Community 193 - "Backup And Restore Database"
Cohesion: 0.20
Nodes (10): Backup, Backup And Restore Database, Linux note, Provided scripts, Recommended strategy, Recovery expectations, Restore, Suggested production routine (+2 more)

### Community 194 - "Desktop App Guide"
Cohesion: 0.20
Nodes (10): Build, Configuration, Desktop App Guide, Discord ID, Entry Points, Environment, Hotkeys, Main Panel (+2 more)

### Community 195 - "Codacy Rules"
Cohesion: 0.20
Nodes (9): After every response, Codacy Rules, CRITICAL: After ANY successful `edit_file` or `reapply` operation, CRITICAL: Dependencies and Security Checks, General, Trying to call a tool that needs a rootPath as a parameter, When there are no Codacy MCP Server tools available, or the MCP Server is not reachable, When you tried to run the `codacy_cli_analyze` tool and the Codacy CLI is not installed (+1 more)

### Community 196 - "PULL_REQUEST_TEMPLATE.md"
Cohesion: 0.20
Nodes (9): Architecture Impact, Change Type, Documentation Impact, Notes, Related Issues, Risks and Review Focus, Screenshots or Recordings, Summary (+1 more)

### Community 197 - "ConfigDialogsPresenter"
Cohesion: 0.22
Nodes (6): ConfigDialogsPresenter, DialogFeedback, User-facing dialog feedback., Build dialog messages and form results for Desktop App configuration UIs., test_config_dialogs_presenter_builds_initial_setup_result(), test_config_dialogs_presenter_validates_initial_setup()

### Community 198 - "Explicit Contracts Guide"
Cohesion: 0.22
Nodes (8): DTO Vs `Protocol`, Explicit Contracts Guide, Goal, Keep Dynamic Details At The Edge, Practical Rule Of Thumb, Smells That Indicate An Implicit Contract, When A Contract Should Be Explicit, When `dict` Is Fine

### Community 199 - "Shared Vs Runtime-Only Decision Guide"
Cohesion: 0.22
Nodes (8): Default Rule, Fast Decision Questions, Good Runtime-Only Candidates, Good Shared Candidates, Practical Rule Of Thumb, Shared Vs Runtime-Only Decision Guide, Smells That Say "Keep This Runtime-Specific", Smells That Say "Move This To Shared"

### Community 200 - "Staging And Rollback"
Cohesion: 0.22
Nodes (9): Application Versioning, Done Criteria, Production Deploy, Rollback, Rollback Point, Staging And Rollback, Staging Baseline, Staging Environment (+1 more)

### Community 201 - "Windows Build Guide"
Cohesion: 0.22
Nodes (8): Compile For Windows, Desktop App Clean Architecture, Distribution, Executable Location, Prerequisites, Troubleshooting, Use The Executable, Windows Build Guide

### Community 202 - "Bot/Desktop HTTP Contract"
Cohesion: 0.25
Nodes (7): Bot/Desktop HTTP Contract, Endpoints, `GET /health`, `GET /voice-context`, Implementation rule, `POST /speak`, Why this exists

### Community 203 - "Environment Configuration"
Cohesion: 0.25
Nodes (8): Bundled Docker + Postgres + Redis Stack, Cloud Production, Environment Configuration, Environment Inventory, Environment Summary, Local Development, Local Postgres Only, Runtime Sources

### Community 204 - "Baseline And Release Gates"
Cohesion: 0.25
Nodes (8): Baseline And Release Gates, Branch protection expectation, Desktop app, Discord bot, Initial SLI And SLO Baseline, Notes, Release Gates, Success Criteria

### Community 205 - "Documentation"
Cohesion: 0.25
Nodes (8): Conventions, Documentation, Getting Started, Governance, Maintenance, Navigation, Operate And Deploy, Understand The System

### Community 206 - "server.py"
Cohesion: 0.25
Nodes (4): _append_vary_origin(), _null_span_context, HTTP server using aiohttp., Version information for the Discord bot and Desktop App.

### Community 207 - "Kubernetes Manifests"
Cohesion: 0.29
Nodes (6): Database Schema, GitOps, Kubernetes Manifests, Local Validation, Overlays, Secret Handling

### Community 208 - "Architecture Transitions"
Cohesion: 0.29
Nodes (6): Architecture Transitions, Bad repository-specific examples, Good repository-specific examples, How to use this guide, Typical transition shapes in this repository, Where transitions usually belong

### Community 210 - "Mutation Testing"
Cohesion: 0.40
Nodes (4): Current CI Limitation, Local Run, Mutation Testing, Scope

### Community 213 - "Documentation Organization"
Cohesion: 0.50
Nodes (3): Documentation Organization, Quick examples, Rules

## Ambiguous Edges - Review These
- `Provider Adoption Rule` → `render.yaml`  [AMBIGUOUS]
  render.yaml · relation: conceptually_related_to

## Knowledge Gaps
- **684 isolated node(s):** `tts-hotkey-windows`, `Dependency Rules`, `Pull Request Checklist`, `Adding Features`, `What Not To Do` (+679 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **303 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Provider Adoption Rule` and `render.yaml`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `TTSConfig` connect `Core Entities & Config` to `Desktop App Configuration`, `TTS Queue Orchestrator & Security`, `Audio Queue Status Interface`, `Core Interfaces & Telemetry`, `Redis Audio Queue`, `Bot Queue Worker`, `Desktop Hotkey Backend`, `TTS Audio Engines`, `Bot Settings & Runtime Config`, `Config Migration to Postgres`, `Desktop TTS Status Gateway`, `Hotkey Monitoring Service`, `Desktop Discord Bot Client`, `Voice Channel Resolution`, `Discord Voice Channel Interfaces`, `Desktop HTTP Bot Client`, `Pyttsx3 TTS Adapter`, `Speak HTTP Controller`, `In-Memory Config Repository`, `__init__.py`, `Desktop Config Validation`, `Runtime Telemetry Spans`, `Voice Context Query DTOs`, `settings.py`, `.handle`, `Mock Audio Queue Tests`, `Core Entities Tests`, `System Tray Notification Service`, `Voice Context Controller`, `Discord Speak Request Builder`, `Desktop Discord Bot Client Requests`, `In-Memory Runtime Telemetry`, `Desktop App Status DTOs`, `Bot Dependency Readiness DTO`?**
  _High betweenness centrality (0.214) - this node is a cross-community bridge._
- **Why does `DesktopAppConfig` connect `Desktop Config Validation` to `Desktop App Configuration`, `OTel Collector Pipeline`, `Desktop Config Environment`, `Desktop Main Window GUI`, `Desktop Hotkey Backend`, `Desktop TTS Bot Client`, `Desktop Config Dialog Helpers`, `Hotkey Monitoring Service`, `Desktop Bot Gateway`, `Desktop Discord Bot Client`, `Desktop App Status Builder`, `TTS Voice Catalog Runtime`, `Postgres Config Storage`, `Desktop UI Configuration Coordinator`, `Core Entities & Config`, `Notification Service Protocol`, `System Tray Notifications`, `Desktop Settings Dialog`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `OpenTelemetryRuntime` connect `OpenTelemetry Audio Queue` to `queue_worker.py`, `OpenTelemetry Fake Exporters`, `Redis Audio Queue`, `Voice Channel Use Cases`, `Bot Queue Worker`, `OpenTelemetry Fake Meters`, `Voice Context Controller`, `Bot Runtime Container`, `Config Migration to Postgres`, `server.py`, `HTTP Server Observability`, `Speak HTTP Controller`, `Infrastructure HTTP Server`, `OpenTelemetry Fake Spans`, `Desktop Config Paths`, `OpenTelemetry Fake Providers`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `TTSConfig` (e.g. with `DiscordSpeakPreparationResult` and `DiscordSpeakRequestBuilder`) actually correct?**
  _`TTSConfig` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 36 inferred relationships involving `AudioQueueItem` (e.g. with `SpeakTextUseCase` and `BotRuntimeTelemetry`) actually correct?**
  _`AudioQueueItem` has 36 INFERRED edges - model-reasoned connections that need verification._
- **Are the 34 inferred relationships involving `TTSRequest` (e.g. with `SpeakTextUseCase` and `BotRuntimeTelemetry`) actually correct?**
  _`TTSRequest` has 34 INFERRED edges - model-reasoned connections that need verification._