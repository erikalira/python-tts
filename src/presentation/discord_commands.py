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
                    await interaction.edit_original_response(content='Joined your channel.')
                else:
                    await interaction.edit_original_response(content='Could not find voice channel.')
            except Exception as e:
                logger.error(f"[JOIN] Error joining channel: {e}", exc_info=True)
                error_msg = str(e).lower()
                
                # Simple error handling
                try:
                    if 'interpreter shutdown' in error_msg or 'cannot schedule new futures' in error_msg:
                        await self._send_bot_inactive_message(interaction)
                    else:
                        await interaction.edit_original_response(content='❌ Não foi possível entrar no canal. Tente novamente.')
                except:
                    logger.error(f"[JOIN] Failed to send error response")
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
        """Handle /speak command.
        
        CRITICAL: Validates guild_id and member info for security isolation.
        """
        logger.info(f"[SPEAK] Command from user {interaction.user.id} ({interaction.user.name}) in guild {interaction.guild.id if interaction.guild else 'None'}")
        await interaction.response.defer(ephemeral=True, thinking=True)
        
        if not HAS_PYNACL or not HAS_FFMPEG:
            logger.warning("[SPEAK] Missing PyNaCl or FFmpeg dependencies")
            await interaction.edit_original_response(
                content='PyNaCl and FFmpeg são necessários para suporte a voz.'
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
                if result.get("queued"):
                    # Show queue position with formatted message
                    await interaction.edit_original_response(
                        content=result["message"]
                    )
                elif result["success"]:
                    # Delete the thinking message on success (audio played)
                    await interaction.delete_original_response()
                else:
                    # Show error message
                    await interaction.edit_original_response(content=result["message"])
                    
            except Exception as msg_error:
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
                    await interaction.edit_original_response(content=f'❌ Erro inesperado')
            except:
                # If we can't send error message, just log it
                logger.debug(f"[SPEAK] Could not send error message")
    
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
        embed.add_field(
            name="Commands",
            value="• `/join` - Join your voice channel\n• `/leave` - Leave voice channel\n"
                  "• `/speak` - Speak text\n• `/config` - Configure TTS settings\n• `/about` - Show this info",
            inline=False
        )
        embed.set_footer(text=f"Running on {platform.system()} {platform.release()}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
