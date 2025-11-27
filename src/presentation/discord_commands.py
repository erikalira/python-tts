"""Discord bot commands."""
import logging
import discord
from discord import app_commands
from src.application.use_cases import SpeakTextUseCase, ConfigureTTSUseCase
from src.core.entities import TTSRequest
import shutil

logger = logging.getLogger(__name__)

# Check dependencies
HAS_FFMPEG = shutil.which('ffmpeg') is not None
try:
    import nacl
    HAS_PYNACL = True
except ImportError:
    HAS_PYNACL = False


class DiscordCommands:
    """Discord slash commands handler.
    
    Follows Single Responsibility: only handles Discord command interface.
    Business logic delegated to use cases.
    """
    
    def __init__(
        self,
        tree: app_commands.CommandTree,
        speak_use_case: SpeakTextUseCase,
        config_use_case: ConfigureTTSUseCase,
        channel_repository
    ):
        """Initialize commands with dependencies.
        
        Args:
            tree: Discord command tree
            speak_use_case: Use case for speaking
            config_use_case: Use case for configuration
            channel_repository: Voice channel repository
        """
        self._tree = tree
        self._speak_use_case = speak_use_case
        self._config_use_case = config_use_case
        self._channel_repository = channel_repository
        
        # Register commands
        self._register_commands()
    
    def _register_commands(self):
        """Register all slash commands."""
        
        @self._tree.command(name='join', description='Make the bot join your voice channel')
        async def join(interaction: discord.Interaction):
            await self._handle_join(interaction)
        
        @self._tree.command(name='leave', description='Make the bot leave the voice channel')
        async def leave(interaction: discord.Interaction):
            await self._handle_leave(interaction)
        
        @self._tree.command(name='speak', description='Make the bot speak the given text in voice channel')
        @app_commands.describe(text='Text to speak')
        async def speak(interaction: discord.Interaction, text: str):
            await self._handle_speak(interaction, text)
        
        @self._tree.command(name='config', description='Configure your personal TTS settings')
        @app_commands.describe(
            engine='TTS engine: gtts (Google TTS, best quality) or pyttsx3 (espeak-ng, offline)',
            language='Language code for gTTS (pt, en, es, fr, etc.) or leave empty',
            voice_id='Voice ID for pyttsx3/espeak-ng (e.g., roa/pt-br, en-us) or leave empty'
        )
        async def config(
            interaction: discord.Interaction,
            engine: str = None,
            language: str = None,
            voice_id: str = None
        ):
            await self._handle_config(interaction, engine, language, voice_id)
        
        @self._tree.command(name='about', description='Show bot information and version')
        async def about(interaction: discord.Interaction):
            await self._handle_about(interaction)
    
    async def _handle_join(self, interaction: discord.Interaction):
        """Handle /join command."""
        if not HAS_PYNACL:
            await interaction.response.send_message(
                'PyNaCl is required for voice support. Install it with `pip install pynacl`.',
                ephemeral=True
            )
            return
        
        member = interaction.user
        if not isinstance(member, discord.Member) and interaction.guild:
            member = interaction.guild.get_member(member.id)
        
        if member and member.voice and member.voice.channel:
            await interaction.response.defer(ephemeral=True)
            try:
                channel = await self._channel_repository.find_by_channel_id(member.voice.channel.id)
                if channel:
                    await channel.connect()
                    await interaction.followup.send('Joined your channel.', ephemeral=True)
                else:
                    await interaction.followup.send('Could not find voice channel.', ephemeral=True)
            except Exception as e:
                await interaction.followup.send(f'Could not join channel: {e}', ephemeral=True)
        else:
            await interaction.response.send_message(
                'You are not connected to a voice channel.',
                ephemeral=True
            )
    
    async def _handle_leave(self, interaction: discord.Interaction):
        """Handle /leave command."""
        if interaction.guild and interaction.guild.voice_client:
            try:
                await interaction.guild.voice_client.disconnect()
                await interaction.response.send_message('Disconnected.', ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f'Error disconnecting: {e}', ephemeral=True)
        else:
            await interaction.response.send_message(
                'I am not connected to a voice channel.',
                ephemeral=True
            )
    
    async def _handle_speak(self, interaction: discord.Interaction, text: str):
        """Handle /speak command."""
        logger.info(f"[SPEAK] Command received from user {interaction.user.id} ({interaction.user.name}) with text: {text[:50]}...")
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        if not HAS_PYNACL or not HAS_FFMPEG:
            logger.warning("[SPEAK] Missing PyNaCl or FFmpeg dependencies")
            await interaction.followup.send(
                'PyNaCl and FFmpeg are required for voice support.',
                ephemeral=True
            )
            return
        
        try:
            # Determine channel and member info
            member = interaction.user
            if not isinstance(member, discord.Member) and interaction.guild:
                member = interaction.guild.get_member(member.id)
            
            # Always use interaction.user.id to ensure we have the user ID
            user_id = interaction.user.id
            logger.info(f"[SPEAK] User ID: {user_id}, Member ID: {member.id if member else 'None'}, Guild ID: {interaction.guild.id if interaction.guild else 'None'}")
            
            # Create request (use user_id for member_id to ensure config lookup works)
            tts_request = TTSRequest(
                text=text,
                guild_id=interaction.guild.id if interaction.guild else None,
                member_id=user_id
            )
            
            # Execute use case
            logger.info(f"[SPEAK] Executing TTS use case...")
            result = await self._speak_use_case.execute(tts_request)
            logger.info(f"[SPEAK] Use case result: {result}")
            
            if result["success"]:
                await interaction.followup.send('✅ Spoke the text.', ephemeral=True)
            else:
                await interaction.followup.send(f'❌ Error: {result["message"]}', ephemeral=True)
        except Exception as e:
            logger.error(f"[SPEAK] Unexpected error in _handle_speak: {e}", exc_info=True)
            try:
                await interaction.followup.send(f'❌ Unexpected error: {str(e)}', ephemeral=True)
            except Exception as followup_error:
                logger.error(f"[SPEAK] Failed to send error followup: {followup_error}")
    
    async def _handle_config(
        self,
        interaction: discord.Interaction,
        engine: str | None,
        language: str | None,
        voice_id: str | None
    ):
        """Handle /config command."""
        result = self._config_use_case.execute(
            user_id=interaction.user.id,
            engine=engine,
            language=language,
            voice_id=voice_id
        )
        
        if not result["success"]:
            await interaction.response.send_message(
                f'❌ {result["message"]}',
                ephemeral=True
            )
            return
        
        config = result["config"]
        
        # If no parameters, show current config
        if engine is None and language is None and voice_id is None:
            embed = discord.Embed(
                title="🎤 Your TTS Configuration",
                description=f"Personal settings for {interaction.user.mention}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Engine", value=config['engine'].upper(), inline=True)
            embed.add_field(name="Language", value=config['language'], inline=True)
            embed.add_field(name="Voice ID", value=config['voice_id'], inline=True)
            embed.add_field(
                name="How to change",
                value="Use `/config engine:gtts` or `/config engine:pyttsx3 voice_id:roa/pt-br`",
                inline=False
            )
        else:
            # Show success message
            embed = discord.Embed(
                title="✅ TTS Configuration Updated",
                description=f"Your personal settings have been updated",
                color=discord.Color.green()
            )
            embed.add_field(name="Engine", value=config['engine'].upper(), inline=True)
            embed.add_field(name="Language", value=config['language'], inline=True)
            embed.add_field(name="Voice ID", value=config['voice_id'], inline=True)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    async def _handle_about(self, interaction: discord.Interaction):
        """Handle /about command."""
        from src.__version__ import __version__, __author__, __description__
        import platform
        
        embed = discord.Embed(
            title="🤖 TTS Bot Information",
            description=__description__,
            color=discord.Color.blue()
        )
        embed.add_field(name="Version", value=f"`{__version__}`", inline=True)
        embed.add_field(name="Author", value=__author__, inline=True)
        embed.add_field(name="FFmpeg", value="✅ Available" if HAS_FFMPEG else "❌ Not found", inline=True)
        embed.add_field(name="PyNaCl", value="✅ Installed" if HAS_PYNACL else "❌ Not installed", inline=True)
        embed.add_field(
            name="Commands",
            value="• `/join` - Join your voice channel\n• `/leave` - Leave voice channel\n"
                  "• `/speak` - Speak text\n• `/config` - Configure TTS settings\n• `/about` - Show this info",
            inline=False
        )
        embed.set_footer(text=f"Running on {platform.system()} {platform.release()}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
