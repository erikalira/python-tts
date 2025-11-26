"""Dependency injection container.

Follows Dependency Inversion Principle by constructing all dependencies
and injecting them into components.
"""
import discord
from discord import app_commands
from config.settings import Config
from src.core.entities import TTSConfig
from src.application.use_cases import SpeakTextUseCase, ConfigureTTSUseCase
from src.infrastructure.tts.engines import TTSEngineFactory
from src.infrastructure.tts.config_repository import InMemoryConfigRepository
from src.infrastructure.discord.voice_channel import DiscordVoiceChannelRepository
from src.presentation.http_controllers import SpeakController
from src.presentation.discord_commands import DiscordCommands


class Container:
    """Dependency Injection Container.
    
    Centralizes dependency construction and wiring.
    """
    
    def __init__(self, config: Config):
        """Initialize container with configuration.
        
        Args:
            config: Application configuration
        """
        self.config = config
        
        # Discord client
        intents = discord.Intents.default()
        intents.voice_states = True
        self.discord_client = discord.Client(intents=intents)
        self.command_tree = app_commands.CommandTree(self.discord_client)
        
        # Repositories
        self.config_repository = InMemoryConfigRepository(config.tts_config)
        self.voice_channel_repository = DiscordVoiceChannelRepository(self.discord_client)
        
        # TTS Engine (created per request via factory)
        self._tts_engine_factory = TTSEngineFactory()
        
        # Use cases
        self.speak_use_case = SpeakTextUseCase(
            tts_engine=self._create_tts_engine(),
            channel_repository=self.voice_channel_repository,
            config_repository=self.config_repository
        )
        
        self.config_use_case = ConfigureTTSUseCase(
            config_repository=self.config_repository
        )
        
        # Controllers
        self.speak_controller = SpeakController(self.speak_use_case)
        
        # Discord commands
        self.discord_commands = DiscordCommands(
            tree=self.command_tree,
            speak_use_case=self.speak_use_case,
            config_use_case=self.config_use_case,
            channel_repository=self.voice_channel_repository
        )
        
        # Register event handlers
        self._register_events()
    
    def _create_tts_engine(self):
        """Create TTS engine based on configuration."""
        return self._tts_engine_factory.create(self.config.tts_config)
    
    def _register_events(self):
        """Register Discord event handlers."""
        
        @self.discord_client.event
        async def on_ready():
            print(f'✅ Discord bot ready as {self.discord_client.user}')
            print(f'   Connected to {len(self.discord_client.guilds)} guild(s)')
            for guild in self.discord_client.guilds:
                print(f'   - {guild.name} (ID: {guild.id})')
            
            try:
                await self.command_tree.sync()
                print('✅ Slash commands synced')
            except Exception as e:
                print(f'❌ Failed to sync commands: {e}')
        
        @self.discord_client.event
        async def on_voice_state_update(member, before, after):
            """Track member voice state changes to maintain cache."""
            self.voice_channel_repository.update_member_cache(
                member.id,
                after.channel
            )
