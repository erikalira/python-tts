"""Discord bot commands."""
import logging
from importlib.util import find_spec

import discord
from discord import app_commands
from src.application.use_cases import (
    ConfigureTTSUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
    SpeakTextUseCase,
    JOIN_RESULT_MISSING_GUILD_ID,
    JOIN_RESULT_OK,
    JOIN_RESULT_USER_NOT_IN_CHANNEL,
    JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND,
    JOIN_RESULT_VOICE_CONNECTION_FAILED,
    LEAVE_RESULT_MISSING_GUILD_ID,
    LEAVE_RESULT_NOT_CONNECTED,
    LEAVE_RESULT_OK,
    LEAVE_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_CROSS_GUILD_CHANNEL,
    SPEAK_RESULT_MISSING_GUILD_ID,
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_OK,
    SPEAK_RESULT_PLAYBACK_TIMEOUT,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_UNKNOWN_ERROR,
    SPEAK_RESULT_USER_LEFT_CHANNEL,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
    SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
    SPEAK_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_VOICE_PERMISSION_DENIED,
)
from src.core.entities import TTSRequest
import shutil

logger = logging.getLogger(__name__)

# Check dependencies
HAS_FFMPEG = shutil.which('ffmpeg') is not None
HAS_PYNACL = find_spec("nacl") is not None

try:
    import davey  # noqa: F401
    HAS_DAVEY = True
except ImportError:
    HAS_DAVEY = False


def _has_voice_runtime_support() -> bool:
    """Return whether the current environment has the dependencies for Discord voice."""
    return HAS_PYNACL and HAS_DAVEY and HAS_FFMPEG


def _get_voice_dependency_message() -> str:
    """Build a user-facing message describing missing voice dependencies."""
    missing = []
    if not HAS_PYNACL:
        missing.append("PyNaCl")
    if not HAS_DAVEY:
        missing.append("davey")
    if not HAS_FFMPEG:
        missing.append("FFmpeg")

    if not missing:
        return ""

    missing_text = ", ".join(missing)
    return (
        f"{missing_text} são necessários para suporte a voz nesta versão do Discord. "
        "Instale as dependências e tente novamente."
    )


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
        join_use_case: JoinVoiceChannelUseCase,
        leave_use_case: LeaveVoiceChannelUseCase,
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
        self._join_use_case = join_use_case
        self._leave_use_case = leave_use_case
        
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
            voz='Escolha a voz do TTS',
            idioma='Escolha o idioma (apenas para Mulher do Google)',
            sotaque='Escolha o sotaque (apenas para R.E.P.O.)'
        )
        @app_commands.choices(voz=[
            app_commands.Choice(name='Mulher do Google (melhor qualidade)', value='gtts'),
            app_commands.Choice(name='R.E.P.O. (robótico, mais rápido)', value='pyttsx3')
        ])
        @app_commands.choices(idioma=[
            app_commands.Choice(name='Português', value='pt'),
            app_commands.Choice(name='Inglês', value='en'),
            app_commands.Choice(name='Espanhol', value='es'),
            app_commands.Choice(name='Francês', value='fr'),
            app_commands.Choice(name='Alemão', value='de'),
            app_commands.Choice(name='Italiano', value='it'),
            app_commands.Choice(name='Japonês', value='ja'),
            app_commands.Choice(name='Coreano', value='ko'),
            app_commands.Choice(name='Chinês', value='zh')
        ])
        @app_commands.choices(sotaque=[
            app_commands.Choice(name='Português (Brasil)', value='roa/pt-br'),
            app_commands.Choice(name='Inglês (EUA)', value='en-us'),
            app_commands.Choice(name='Inglês (Reino Unido)', value='en-gb'),
            app_commands.Choice(name='Espanhol', value='roa/es'),
            app_commands.Choice(name='Francês', value='roa/fr')
        ])
        async def config(
            interaction: discord.Interaction,
            voz: str = None,
            idioma: str = None,
            sotaque: str = None
        ):
            await self._handle_config(interaction, voz, idioma, sotaque)
        
        @self._tree.command(name='about', description='Show bot information and version')
        async def about(interaction: discord.Interaction):
            await self._handle_about(interaction)
    
    async def _send_bot_inactive_message(self, interaction: discord.Interaction) -> bool:
        """Send message about bot being inactive with Render reactivation link.
        
        Returns:
            True if message was sent successfully, False otherwise.
        """
        try:
            await interaction.edit_original_response(
                content='❌ **Bot está desligando ou inativo!**\n\n'
                '🔄 Para reativar o bot, acesse:\n'
                '**https://python-tts-s3z8.onrender.com/**\n\n'
                '_(O servidor gratuito do Render desliga após inatividade)_'
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send bot inactive message: {e}")
            return False
    
    async def _handle_join(self, interaction: discord.Interaction):
        """Handle /join command."""
        if not _has_voice_runtime_support():
            await interaction.response.send_message(
                _get_voice_dependency_message(),
                ephemeral=True
            )
            return
        
        guild_id = interaction.guild.id if interaction.guild else None
        member_id = interaction.user.id if interaction.user else None

        await interaction.response.defer(ephemeral=True)
        result = await self._join_use_case.execute(guild_id=guild_id, member_id=member_id)

        if result.get("code") == JOIN_RESULT_OK:
            await interaction.edit_original_response(content='Joined your channel.')
            return

        if result.get("code") == JOIN_RESULT_USER_NOT_IN_CHANNEL:
            await interaction.edit_original_response(
                'You are not connected to a voice channel.',
            )
            return

        if result.get("code") == JOIN_RESULT_MISSING_GUILD_ID:
            await interaction.edit_original_response(content='❌ Este comando só pode ser usado em um servidor.')
            return

        if result.get("code") == JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND:
            await interaction.edit_original_response(content='Could not find voice channel.')
            return

        if result.get("code") == JOIN_RESULT_VOICE_CONNECTION_FAILED:
            error_msg = result.get("error_detail", "").lower()
            if 'interpreter shutdown' in error_msg or 'cannot schedule new futures' in error_msg:
                await self._send_bot_inactive_message(interaction)
            else:
                await interaction.edit_original_response(content='❌ Não foi possível entrar no canal. Tente novamente.')
            return

        await interaction.edit_original_response(content='❌ Não foi possível entrar no canal. Tente novamente.')
    
    async def _handle_leave(self, interaction: discord.Interaction):
        """Handle /leave command."""
        guild_id = interaction.guild.id if interaction.guild else None
        result = await self._leave_use_case.execute(guild_id=guild_id)

        if result.get("code") == LEAVE_RESULT_OK:
            await interaction.response.send_message('Disconnected.', ephemeral=True)
            return

        if result.get("code") == LEAVE_RESULT_NOT_CONNECTED:
            await interaction.response.send_message(
                'I am not connected to a voice channel.',
                ephemeral=True
            )
            return

        if result.get("code") == LEAVE_RESULT_MISSING_GUILD_ID:
            await interaction.response.send_message(
                '❌ Este comando só pode ser usado em um servidor.',
                ephemeral=True
            )
            return

        if result.get("code") == LEAVE_RESULT_VOICE_CONNECTION_FAILED:
            detail = result.get("error_detail")
            if detail:
                await interaction.response.send_message(f'Error disconnecting: {detail}', ephemeral=True)
            else:
                await interaction.response.send_message('Error disconnecting.', ephemeral=True)
            return

        await interaction.response.send_message('Error disconnecting.', ephemeral=True)
    
    async def _handle_speak(self, interaction: discord.Interaction, text: str):
        """Handle /speak command.
        
        CRITICAL: Validates guild_id and member info for security isolation.
        """
        logger.info(f"[SPEAK] Command from user {interaction.user.id} ({interaction.user.name}) in guild {interaction.guild.id if interaction.guild else 'None'}")
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        if not _has_voice_runtime_support():
            logger.warning("[SPEAK] Missing PyNaCl, davey or FFmpeg dependencies")
            await interaction.edit_original_response(
                content=_get_voice_dependency_message()
            )
            return
        
        try:
            # VALIDATION: Ensure guild is set (critical for multi-server isolation)
            if not interaction.guild or not interaction.guild.id:
                logger.error("[SPEAK] SECURITY: No guild ID available")
                await interaction.edit_original_response(
                    content='❌ Erro: Não foi possível determinar o servidor.'
                )
                return
            
            guild_id = interaction.guild.id
            member_id = interaction.user.id
            
            logger.info(f"[SPEAK] Guild: {guild_id}, Member: {member_id}, Text: {text[:50]}...")
            
            # Create request with BOTH guild_id and member_id
            tts_request = TTSRequest(
                text=text,
                guild_id=guild_id,  # CRITICAL: Server isolation
                member_id=member_id
            )
            
            # Execute use case
            result = await self._speak_use_case.execute(tts_request)
            
            # Handle response based on queue status
            try:
                if result.get("code") == SPEAK_RESULT_QUEUED:
                    # Show queue position with formatted message
                    await interaction.edit_original_response(
                        content=self._build_speak_message(result)
                    )
                elif result.get("code") == SPEAK_RESULT_OK:
                    # Delete the thinking message on success (audio played)
                    await interaction.delete_original_response()
                else:
                    # Show error message
                    await interaction.edit_original_response(
                        content=self._build_speak_message(result)
                    )
                    
            except discord.HTTPException as msg_error:
                # Ignore message update errors - audio already played or failed
                logger.debug(f"[SPEAK] Could not update interaction message: {msg_error}")
                
        except Exception as e:
            logger.error(f"[SPEAK] Unexpected error: {e}", exc_info=True)
            
            # Try to send error message, but don't fail if we can't
            try:
                error_msg = str(e).lower()
                if 'interpreter shutdown' in error_msg or 'cannot schedule new futures' in error_msg:
                    await interaction.edit_original_response(content='❌ Bot está inativo ou desligando.')
                else:
                    await interaction.edit_original_response(content='❌ Erro inesperado')
            except discord.HTTPException:
                # If we can't send error message, just log it
                logger.debug("[SPEAK] Could not send error message")

    def _build_speak_message(self, result: dict) -> str:
        """Map a neutral application result to a Discord-facing message."""
        code = result.get("code")
        if code == SPEAK_RESULT_QUEUED:
            position = result.get("position", 0) + 1
            queue_size = result.get("queue_size", position)
            return f"⏳ Sua mensagem está na **fila** (posição **{position}**/{queue_size}). Será reproduzida em breve!"
        if code == SPEAK_RESULT_MISSING_TEXT:
            return "❌ Texto não informado."
        if code == SPEAK_RESULT_USER_NOT_IN_CHANNEL:
            return "❌ Você não está em nenhuma sala de voz. Entre em uma sala e tente novamente."
        if code == SPEAK_RESULT_QUEUE_FULL:
            return "❌ Fila de áudio cheia. Tente novamente mais tarde."
        if code == SPEAK_RESULT_MISSING_GUILD_ID:
            return "❌ Erro: Não foi possível determinar o servidor."
        if code == SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND:
            return "❌ Bot não conseguiu encontrar sua sala de voz."
        if code == SPEAK_RESULT_CROSS_GUILD_CHANNEL:
            return "❌ Canal de voz pertence a servidor diferente."
        if code == SPEAK_RESULT_USER_LEFT_CHANNEL:
            return "❌ Você saiu do canal de voz."
        if code == SPEAK_RESULT_PLAYBACK_TIMEOUT:
            return "⏱️ Tempo limite excedido durante reprodução."
        if code == SPEAK_RESULT_VOICE_CONNECTION_FAILED:
            return "🔌 Bot não conseguiu se conectar ao canal."
        if code == SPEAK_RESULT_VOICE_PERMISSION_DENIED:
            return "⛔ Bot não tem permissão neste canal."
        if code == SPEAK_RESULT_UNKNOWN_ERROR:
            return "❌ Erro ao reproduzir áudio."
        return "❌ Erro inesperado ao processar áudio."
    
    async def _handle_config(
        self,
        interaction: discord.Interaction,
        voz: str | None,
        idioma: str | None,
        sotaque: str | None
    ):
        """Handle /config command.
        
        CRITICAL: Uses guild_id for server-specific configuration.
        """
        # VALIDATION: Ensure guild is set
        if not interaction.guild or not interaction.guild.id:
            await interaction.response.send_message(
                '❌ Este comando só pode ser usado em um servidor.',
                ephemeral=True
            )
            return
        
        guild_id = interaction.guild.id
        user_id = interaction.user.id
        
        logger.info(f"[CONFIG] User {user_id} in guild {guild_id} updating config: voz={voz}, idioma={idioma}, sotaque={sotaque}")
        
        # If no changes, get current config
        if voz is None and idioma is None and sotaque is None:
            result = self._config_use_case.get_config(guild_id)
            
            if not result["success"]:
                await interaction.response.send_message(
                    f'❌ {result["message"]}',
                    ephemeral=True
                )
                return
            
            config = result["config"]
            voz_nome = "Mulher do Google" if config['engine'] == 'gtts' else "R.E.P.O. (robótico)"
            
            embed = discord.Embed(
                title="🎤 Configuração de Voz do Servidor",
                description=f"Configurações de {interaction.guild.name}",
                color=discord.Color.blue()
            )
            embed.add_field(name="Voz", value=voz_nome, inline=True)
            embed.add_field(name="Idioma", value=config['language'].upper(), inline=True)
            embed.add_field(name="Sotaque", value=config['voice_id'], inline=True)
            embed.add_field(name="Taxa de Fala", value=str(config['rate']), inline=True)
            embed.set_footer(text=f"Servidor (Guild ID: {guild_id})")
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Update configuration asynchronously with persistence
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        try:
            result = await self._config_use_case.update_config_async(
                guild_id=guild_id,
                engine=voz,
                language=idioma,
                voice_id=sotaque
            )
            
            if not result["success"]:
                await interaction.edit_original_response(content=f'❌ {result["message"]}')
                return
            
            config = result["config"]
            voz_nome = "Mulher do Google" if config['engine'] == 'gtts' else "R.E.P.O. (robótico)"
            
            embed = discord.Embed(
                title="✅ Configuração Atualizada",
                description=f"Configurações do servidor {interaction.guild.name} atualizadas",
                color=discord.Color.green()
            )
            embed.add_field(name="Voz", value=voz_nome, inline=True)
            embed.add_field(name="Idioma", value=config['language'].upper(), inline=True)
            embed.add_field(name="Sotaque", value=config['voice_id'], inline=True)
            embed.set_footer(text=f"Servidor (Guild ID: {guild_id})")
            
            await interaction.edit_original_response(embed=embed)
            
        except Exception as e:
            logger.error(f"[CONFIG] Error updating config for guild {guild_id}: {e}", exc_info=True)
            await interaction.edit_original_response(content='❌ Erro ao atualizar configuração')
    
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
        embed.add_field(name="davey", value="✅ Installed" if HAS_DAVEY else "❌ Not installed", inline=True)
        embed.add_field(
            name="Commands",
            value="• `/join` - Join your voice channel\n• `/leave` - Leave voice channel\n"
                  "• `/speak` - Speak text\n• `/config` - Configure TTS settings\n• `/about` - Show this info",
            inline=False
        )
        embed.set_footer(text=f"Running on {platform.system()} {platform.release()}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
