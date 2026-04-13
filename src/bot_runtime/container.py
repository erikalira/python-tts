"""Dependency injection container."""

import importlib.util
import logging

import discord
from discord import app_commands

from src.application.tts_queue_orchestrator import TTSQueueOrchestrator
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.application.use_cases import (
    ConfigureTTSUseCase,
    GetCurrentVoiceContextUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
    SpeakTextUseCase,
)
from src.infrastructure.audio_queue import InMemoryAudioQueue
from src.infrastructure.discord.voice_runtime import DependencyVoiceRuntimeAvailability
from src.infrastructure.discord.voice_channel import DiscordVoiceChannelRepository
from src.infrastructure.persistence.config_storage import GuildConfigRepository, JSONConfigStorage
from src.infrastructure.persistence.postgres_storage import PostgreSQLConfigStorage
from src.infrastructure.tts.audio_cleanup import FileAudioCleanup
from src.infrastructure.tts.engines import RoutedTTSEngine
from src.infrastructure.tts.voice_catalog import RuntimeTTSCatalog
from src.presentation.discord_commands import DiscordCommands
from src.presentation.http_controllers import SpeakController, VoiceContextController

from .settings import Config

logger = logging.getLogger(__name__)


class Container:
    """Centralize dependency construction and wiring."""

    def __init__(self, config: Config):
        self.config = config
        self._commands_synced = False
        intents = discord.Intents.default()
        intents.voice_states = True
        self.discord_client = discord.Client(intents=intents)
        self.command_tree = app_commands.CommandTree(self.discord_client)

        config_storage = self._build_config_storage(config)
        self.config_repository = GuildConfigRepository(default_config=config.tts_config, storage=config_storage)
        self.voice_channel_repository = DiscordVoiceChannelRepository(
            self.discord_client,
            connection_timeout_seconds=config.voice_connection_timeout_seconds,
            playback_timeout_seconds=config.tts_playback_timeout_seconds,
            idle_disconnect_timeout_seconds=config.voice_idle_disconnect_timeout_seconds,
        )
        self.audio_queue = InMemoryAudioQueue()
        self.audio_cleanup = FileAudioCleanup()
        self.tts_engine = RoutedTTSEngine()
        self.tts_catalog = RuntimeTTSCatalog()
        self.voice_channel_resolution = VoiceChannelResolutionService(self.voice_channel_repository)
        self.tts_queue_orchestrator = TTSQueueOrchestrator(
            tts_engine=self.tts_engine,
            config_repository=self.config_repository,
            audio_queue=self.audio_queue,
            voice_channel_resolution=self.voice_channel_resolution,
            audio_cleanup=self.audio_cleanup,
            generation_timeout_seconds=config.tts_generation_timeout_seconds,
            playback_timeout_seconds=config.tts_playback_timeout_seconds,
        )

        self.speak_use_case = SpeakTextUseCase(
            channel_repository=self.voice_channel_repository,
            audio_queue=self.audio_queue,
            max_text_length=config.max_text_length,
            voice_channel_resolution=self.voice_channel_resolution,
            queue_orchestrator=self.tts_queue_orchestrator,
        )
        self.config_use_case = ConfigureTTSUseCase(config_repository=self.config_repository)
        self.join_use_case = JoinVoiceChannelUseCase(channel_repository=self.voice_channel_repository)
        self.leave_use_case = LeaveVoiceChannelUseCase(channel_repository=self.voice_channel_repository)
        self.voice_context_use_case = GetCurrentVoiceContextUseCase(channel_repository=self.voice_channel_repository)

        self.speak_controller = SpeakController(self.speak_use_case, self.config_repository)
        self.voice_context_controller = VoiceContextController(self.voice_context_use_case)
        self.voice_runtime_availability = DependencyVoiceRuntimeAvailability()
        self.discord_commands = DiscordCommands(
            tree=self.command_tree,
            speak_use_case=self.speak_use_case,
            config_use_case=self.config_use_case,
            join_use_case=self.join_use_case,
            leave_use_case=self.leave_use_case,
            voice_runtime_availability=self.voice_runtime_availability,
            tts_catalog=self.tts_catalog,
        )

        self._log_voice_runtime_status()
        self._register_events()

    def _build_config_storage(self, config: Config):
        if config.config_storage_backend == "postgres":
            logger.info("[CONTAINER] Using Postgres config storage")
            return PostgreSQLConfigStorage(database_url=config.database_url or "")

        logger.info("[CONTAINER] Using JSON config storage at %s", config.config_storage_dir)
        return JSONConfigStorage(storage_dir=config.config_storage_dir)

    def _log_voice_runtime_status(self) -> None:
        has_davey = importlib.util.find_spec("davey") is not None
        if not has_davey:
            logger.warning("Voice support requires the `davey` package with newer discord.py versions.")

    def _register_events(self):
        @self.discord_client.event
        async def on_ready():
            logger.info("Discord bot ready as %s", self.discord_client.user)
            logger.info("Connected to %s guild(s)", len(self.discord_client.guilds))
            for guild in self.discord_client.guilds:
                logger.info("Guild connected: %s (ID: %s)", guild.name, guild.id)
            await self._sync_commands_once()

        @self.discord_client.event
        async def on_voice_state_update(member, before, after):
            self.voice_channel_repository.update_member_cache(member.id, after.channel)

    async def _sync_commands_once(self) -> None:
        """Sync slash commands only once per process to avoid reconnect churn."""
        if self._commands_synced:
            logger.info("Slash commands already synced for this process")
            return

        try:
            await self.command_tree.sync()
            self._commands_synced = True
            logger.info("Slash commands synced")
        except Exception as exc:
            logger.error("Failed to sync commands: %s", exc)
