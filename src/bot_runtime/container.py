"""Dependency injection container."""

import importlib.util

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
from src.infrastructure.discord.voice_channel import DiscordVoiceChannelRepository
from src.infrastructure.persistence.config_storage import GuildConfigRepository, JSONConfigStorage
from src.infrastructure.tts.audio_cleanup import FileAudioCleanup
from src.infrastructure.tts.engines import TTSEngineFactory
from src.presentation.discord_commands import DiscordCommands
from src.presentation.http_controllers import SpeakController, VoiceContextController

from .settings import Config


class Container:
    """Centralize dependency construction and wiring."""

    def __init__(self, config: Config):
        self.config = config
        intents = discord.Intents.default()
        intents.voice_states = True
        self.discord_client = discord.Client(intents=intents)
        self.command_tree = app_commands.CommandTree(self.discord_client)

        json_storage = JSONConfigStorage(storage_dir="configs")
        self.config_repository = GuildConfigRepository(default_config=config.tts_config, storage=json_storage)
        self.voice_channel_repository = DiscordVoiceChannelRepository(self.discord_client)
        self.audio_queue = InMemoryAudioQueue()
        self.audio_cleanup = FileAudioCleanup()
        self.tts_engine_factory = TTSEngineFactory()
        self.tts_engine = self.tts_engine_factory.create(config.tts_config)
        self.voice_channel_resolution = VoiceChannelResolutionService(self.voice_channel_repository)
        self.tts_queue_orchestrator = TTSQueueOrchestrator(
            tts_engine=self.tts_engine,
            config_repository=self.config_repository,
            audio_queue=self.audio_queue,
            voice_channel_resolution=self.voice_channel_resolution,
            audio_cleanup=self.audio_cleanup,
        )

        self.speak_use_case = SpeakTextUseCase(
            tts_engine=self.tts_engine,
            channel_repository=self.voice_channel_repository,
            config_repository=self.config_repository,
            audio_queue=self.audio_queue,
            audio_cleanup=self.audio_cleanup,
            max_text_length=config.max_text_length,
            voice_channel_resolution=self.voice_channel_resolution,
            queue_orchestrator=self.tts_queue_orchestrator,
        )
        self.config_use_case = ConfigureTTSUseCase(config_repository=self.config_repository)
        self.join_use_case = JoinVoiceChannelUseCase(channel_repository=self.voice_channel_repository)
        self.leave_use_case = LeaveVoiceChannelUseCase(channel_repository=self.voice_channel_repository)
        self.voice_context_use_case = GetCurrentVoiceContextUseCase(channel_repository=self.voice_channel_repository)

        self.speak_controller = SpeakController(self.speak_use_case)
        self.voice_context_controller = VoiceContextController(self.voice_context_use_case)
        self.discord_commands = DiscordCommands(
            tree=self.command_tree,
            speak_use_case=self.speak_use_case,
            config_use_case=self.config_use_case,
            join_use_case=self.join_use_case,
            leave_use_case=self.leave_use_case,
        )

        self._log_voice_runtime_status()
        self._register_events()

    def _log_voice_runtime_status(self) -> None:
        has_davey = importlib.util.find_spec("davey") is not None
        if not has_davey:
            print("Warning: voice support requires the `davey` package with newer discord.py versions.")

    def _register_events(self):
        @self.discord_client.event
        async def on_ready():
            print(f"Discord bot ready as {self.discord_client.user}")
            print(f"   Connected to {len(self.discord_client.guilds)} guild(s)")
            for guild in self.discord_client.guilds:
                print(f"   - {guild.name} (ID: {guild.id})")
            try:
                await self.command_tree.sync()
                print("Slash commands synced")
            except Exception as exc:
                print(f"Failed to sync commands: {exc}")

        @self.discord_client.event
        async def on_voice_state_update(member, before, after):
            self.voice_channel_repository.update_member_cache(member.id, after.channel)
