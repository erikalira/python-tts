"""Dependency injection container."""

import importlib.util
import inspect
import logging
import os
import uuid
from typing import Any, cast

import discord
from discord import app_commands

from src.application.interface_language_preferences import InterfaceLanguagePreferenceRepository
from src.application.tts_queue_orchestrator import TTSQueueOrchestrator
from src.application.use_cases import (
    ConfigureInterfaceLanguageUseCase,
    ConfigureTTSUseCase,
    GetCurrentVoiceContextUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
    SpeakTextUseCase,
)
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.bot_runtime.queue_worker import BotQueueWorker
from src.bot_runtime.readiness import AudioQueueHealthPort, BotReadinessProbe, ConfigRepositoryHealthPort
from src.core.interfaces import IAudioQueue
from src.infrastructure.audio_queue import InMemoryAudioQueue, RedisAudioQueue
from src.infrastructure.discord.voice_channel import DiscordVoiceChannelRepository
from src.infrastructure.discord.voice_runtime import DependencyVoiceRuntimeAvailability
from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime
from src.infrastructure.persistence.config_storage import GuildConfigRepository, IConfigStorage, JSONConfigStorage
from src.infrastructure.persistence.interface_language_preferences import (
    JSONInterfaceLanguagePreferenceRepository,
    PostgreSQLInterfaceLanguagePreferenceRepository,
)
from src.infrastructure.persistence.postgres_storage import PostgreSQLConfigStorage
from src.infrastructure.rate_limiting import InMemoryRateLimiter
from src.infrastructure.runtime_observability import InMemoryBotRuntimeTelemetry
from src.infrastructure.tts.audio_cleanup import FileAudioCleanup
from src.infrastructure.tts.engines import RoutedTTSEngine
from src.infrastructure.tts.voice_catalog import RuntimeTTSCatalog
from src.presentation.discord_commands import DiscordCommands
from src.presentation.http_controllers import SpeakController, VoiceContextController

from .settings import Config

logger = logging.getLogger(__name__)

try:  # pragma: no cover - exercised when Redis is installed in runtime environments.
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover - unit tests still cover the fallback path.
    Redis = None  # type: ignore[assignment]


class Container:
    """Centralize dependency construction and wiring."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.process_marker = f"pid={os.getpid()} run={uuid.uuid4().hex[:8]}"
        self._commands_synced = False
        intents = discord.Intents.default()
        intents.voice_states = True
        self.discord_client = discord.Client(intents=intents)
        self.command_tree: Any = app_commands.CommandTree(self.discord_client)
        self.otel_runtime: Any = OpenTelemetryRuntime(
            enabled=config.otel_enabled,
            service_name=config.otel_service_name,
            queue_backend=config.tts_queue_backend,
            otlp_endpoint=config.otel_exporter_otlp_endpoint,
        )

        config_storage = self._build_config_storage(config)
        self.config_repository = GuildConfigRepository(default_config=config.tts_config, storage=config_storage)
        self.interface_language_repository = self._build_interface_language_repository(config)
        self.voice_channel_repository = DiscordVoiceChannelRepository(
            self.discord_client,
            connection_timeout_seconds=config.voice_connection_timeout_seconds,
            playback_timeout_seconds=config.tts_playback_timeout_seconds,
            idle_disconnect_timeout_seconds=config.voice_idle_disconnect_timeout_seconds,
        )
        self.audio_queue: Any = self._build_audio_queue(config)
        self.audio_cleanup = FileAudioCleanup()
        self.tts_engine = RoutedTTSEngine()
        self.tts_catalog = RuntimeTTSCatalog()
        self.runtime_telemetry = InMemoryBotRuntimeTelemetry()
        self.rate_limiter = InMemoryRateLimiter()
        self.voice_channel_resolution = VoiceChannelResolutionService(self.voice_channel_repository)
        self.tts_queue_orchestrator = TTSQueueOrchestrator(
            tts_engine=self.tts_engine,
            config_repository=self.config_repository,
            audio_queue=self.audio_queue,
            voice_channel_resolution=self.voice_channel_resolution,
            audio_cleanup=self.audio_cleanup,
            generation_timeout_seconds=config.tts_generation_timeout_seconds,
            playback_timeout_seconds=config.tts_playback_timeout_seconds,
            telemetry=self.runtime_telemetry,
            otel_runtime=self.otel_runtime,
        )
        self.queue_worker: Any = BotQueueWorker(
            audio_queue=self.audio_queue,
            queue_orchestrator=self.tts_queue_orchestrator,
            guild_lock_ttl_seconds=config.queue_guild_lock_ttl_seconds,
            guild_lock_renew_interval_seconds=config.queue_guild_lock_renew_interval_seconds,
            processing_lease_ttl_seconds=config.queue_processing_lease_ttl_seconds,
            processing_lease_renew_interval_seconds=config.queue_processing_lease_renew_interval_seconds,
            otel_runtime=self.otel_runtime,
        )
        self.readiness_probe = BotReadinessProbe(
            config=config,
            discord_client=self.discord_client,
            queue_worker=self.queue_worker,
            config_repository=cast(ConfigRepositoryHealthPort, self.config_repository),
            audio_queue=cast(AudioQueueHealthPort, self.audio_queue),
        )

        self.speak_use_case = SpeakTextUseCase(
            channel_repository=self.voice_channel_repository,
            audio_queue=self.audio_queue,
            max_text_length=config.max_text_length,
            voice_channel_resolution=self.voice_channel_resolution,
            queue_orchestrator=self.tts_queue_orchestrator,
            queue_runtime_is_active=self.queue_worker.is_running,
            telemetry=self.runtime_telemetry,
            otel_runtime=self.otel_runtime,
        )
        self.config_use_case = ConfigureTTSUseCase(config_repository=self.config_repository)
        self.interface_language_use_case = ConfigureInterfaceLanguageUseCase(
            preference_repository=self.interface_language_repository
        )
        self.join_use_case = JoinVoiceChannelUseCase(channel_repository=self.voice_channel_repository)
        self.leave_use_case = LeaveVoiceChannelUseCase(channel_repository=self.voice_channel_repository)
        self.voice_context_use_case = GetCurrentVoiceContextUseCase(channel_repository=self.voice_channel_repository)

        self.speak_controller = SpeakController(
            self.speak_use_case,
            self.config_repository,
            rate_limiter=self.rate_limiter,
            rate_limit_max_requests=config.rate_limit_max_requests,
            rate_limit_window_seconds=config.rate_limit_window_seconds,
            auth_token=config.speak_auth_token,
            max_text_length=config.max_text_length,
            otel_runtime=self.otel_runtime,
        )
        self.voice_context_controller = VoiceContextController(self.voice_context_use_case)
        self.voice_runtime_availability = DependencyVoiceRuntimeAvailability()
        self.discord_commands = DiscordCommands(
            tree=self.command_tree,
            speak_use_case=self.speak_use_case,
            config_use_case=self.config_use_case,
            interface_language_use_case=self.interface_language_use_case,
            join_use_case=self.join_use_case,
            leave_use_case=self.leave_use_case,
            voice_runtime_availability=self.voice_runtime_availability,
            tts_catalog=self.tts_catalog,
            runtime_context_provider=self._runtime_context,
            rate_limiter=self.rate_limiter,
            rate_limit_max_requests=config.rate_limit_max_requests,
            rate_limit_window_seconds=config.rate_limit_window_seconds,
        )

        self._log_voice_runtime_status()
        self._register_events()

    def _build_config_storage(self, config: Config) -> IConfigStorage:
        if config.config_storage_backend == "postgres":
            logger.info("[CONTAINER] Using Postgres config storage")
            return PostgreSQLConfigStorage(database_url=config.database_url or "")

        logger.info("[CONTAINER] Using JSON config storage at %s", config.config_storage_dir)
        return JSONConfigStorage(storage_dir=config.config_storage_dir)

    def _build_interface_language_repository(self, config: Config) -> InterfaceLanguagePreferenceRepository:
        if config.config_storage_backend == "postgres":
            logger.info("[CONTAINER] Using Postgres interface language preference storage")
            return PostgreSQLInterfaceLanguagePreferenceRepository(database_url=config.database_url or "")

        logger.info("[CONTAINER] Using JSON interface language preference storage at %s", config.config_storage_dir)
        return JSONInterfaceLanguagePreferenceRepository(storage_dir=config.config_storage_dir)

    def _build_audio_queue(self, config: Config) -> IAudioQueue:
        otel_runtime = getattr(self, "otel_runtime", None)
        if not isinstance(otel_runtime, OpenTelemetryRuntime):
            otel_runtime = None
        if config.tts_queue_backend == "redis":
            if Redis is None:
                raise RuntimeError("redis package is required for TTS_QUEUE_BACKEND=redis")

            logger.info(
                "[CONTAINER] Using Redis audio queue at %s:%s/%s",
                config.redis_host,
                config.redis_port,
                config.redis_db,
            )
            redis_client = Redis(
                host=config.redis_host,
                port=config.redis_port,
                db=config.redis_db,
                password=config.redis_password,
                decode_responses=False,
            )
            return RedisAudioQueue(
                redis_client,
                max_queue_size=config.tts_queue_max_size,
                key_prefix=config.redis_key_prefix,
                completed_item_ttl_seconds=config.redis_completed_item_ttl_seconds,
                telemetry=otel_runtime,
            )

        logger.info("[CONTAINER] Using in-memory audio queue")
        return InMemoryAudioQueue(
            max_queue_size=config.tts_queue_max_size,
            telemetry=otel_runtime,
        )

    def _log_voice_runtime_status(self) -> None:
        has_davey = importlib.util.find_spec("davey") is not None
        if not has_davey:
            logger.warning("Voice support requires the `davey` package with newer discord.py versions.")

    def _register_events(self) -> None:
        @self.discord_client.event
        async def on_connect() -> None:
            logger.info(
                "[GATEWAY] Connected to Discord gateway | process=%s | session_id=%s",
                self.process_marker,
                self._gateway_session_id(),
            )

        @self.discord_client.event
        async def on_ready() -> None:
            logger.info(
                "Discord bot ready as %s | process=%s | session_id=%s",
                self.discord_client.user,
                self.process_marker,
                self._gateway_session_id(),
            )
            logger.info("Connected to %s guild(s)", len(self.discord_client.guilds))
            for guild in self.discord_client.guilds:
                logger.info("Guild connected: %s (ID: %s)", guild.name, guild.id)
            await self._sync_commands_once()
            await self._start_queue_worker_once()

        @self.discord_client.event
        async def on_resumed() -> None:
            logger.info(
                "[GATEWAY] Discord gateway session resumed | process=%s | session_id=%s",
                self.process_marker,
                self._gateway_session_id(),
            )

        @self.discord_client.event
        async def on_disconnect() -> None:
            logger.warning(
                "[GATEWAY] Disconnected from Discord gateway | process=%s | session_id=%s | client_ready=%s",
                self.process_marker,
                self._gateway_session_id(),
                self.discord_client.is_ready(),
            )

        @self.discord_client.event
        async def on_voice_state_update(
            member: discord.Member,
            before: discord.VoiceState,
            after: discord.VoiceState,
        ) -> None:
            del before
            channel = after.channel if isinstance(after.channel, discord.VoiceChannel) else None
            self.voice_channel_repository.update_member_cache(member.id, channel)

    def _gateway_session_id(self) -> str:
        ws = getattr(self.discord_client, "ws", None)
        session_id = getattr(ws, "session_id", None)
        return session_id or "unknown"

    def _runtime_context(self) -> dict[str, str]:
        return {
            "process": self.process_marker,
            "session_id": self._gateway_session_id(),
        }

    async def _sync_commands_once(self) -> None:
        """Sync slash commands only once per process to avoid reconnect churn."""
        if self._commands_synced:
            logger.info("Slash commands already synced for this process")
            return

        try:
            if hasattr(self.command_tree, "set_translator") and hasattr(self, "discord_commands"):
                await self.command_tree.set_translator(self.discord_commands.command_translator())
            await self.command_tree.sync()
            self._commands_synced = True
            logger.info("Slash commands synced")
        except Exception as exc:
            logger.error("Failed to sync commands: %s", exc)

    async def _start_queue_worker_once(self) -> None:
        if self.queue_worker.is_running():
            return
        await self.queue_worker.start()

    async def shutdown(self) -> None:
        if self.queue_worker.is_running():
            await self.queue_worker.stop()
        close_queue = getattr(self.audio_queue, "aclose", None)
        if callable(close_queue):
            close_result = close_queue()
            if inspect.isawaitable(close_result):
                await close_result
        otel_runtime = getattr(self, "otel_runtime", None)
        otel_shutdown = getattr(otel_runtime, "shutdown", None)
        if callable(otel_shutdown):
            otel_shutdown()

    async def readiness_payload(self) -> dict[str, object]:
        return await self.readiness_probe.payload()
