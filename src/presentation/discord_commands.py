"""Discord bot commands."""

import logging
import shutil
from importlib.util import find_spec

import discord
from discord import app_commands

from src.application.results import SPEAK_RESULT_OK, SPEAK_RESULT_QUEUED
from src.application.use_cases import (
    ConfigureTTSUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
    SpeakTextUseCase,
)
from src.core.entities import TTSRequest
from src.presentation.discord_presenters import (
    DiscordJoinPresenter,
    DiscordLeavePresenter,
    DiscordSpeakPresenter,
)

logger = logging.getLogger(__name__)

HAS_FFMPEG = shutil.which("ffmpeg") is not None
HAS_PYNACL = find_spec("nacl") is not None

try:
    import davey  # noqa: F401

    HAS_DAVEY = True
except ImportError:
    HAS_DAVEY = False


def _has_voice_runtime_support() -> bool:
    return HAS_PYNACL and HAS_DAVEY and HAS_FFMPEG


def _get_voice_dependency_message() -> str:
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
    """Discord slash commands handler."""

    def __init__(
        self,
        tree: app_commands.CommandTree,
        speak_use_case: SpeakTextUseCase,
        config_use_case: ConfigureTTSUseCase,
        join_use_case: JoinVoiceChannelUseCase,
        leave_use_case: LeaveVoiceChannelUseCase,
    ):
        self._tree = tree
        self._speak_use_case = speak_use_case
        self._config_use_case = config_use_case
        self._join_use_case = join_use_case
        self._leave_use_case = leave_use_case
        self._join_presenter = DiscordJoinPresenter()
        self._leave_presenter = DiscordLeavePresenter()
        self._speak_presenter = DiscordSpeakPresenter()
        self._register_commands()

    def _register_commands(self):
        @self._tree.command(name="join", description="Make the bot join your voice channel")
        async def join(interaction: discord.Interaction):
            await self._handle_join(interaction)

        @self._tree.command(name="leave", description="Make the bot leave the voice channel")
        async def leave(interaction: discord.Interaction):
            await self._handle_leave(interaction)

        @self._tree.command(name="speak", description="Make the bot speak the given text in voice channel")
        @app_commands.describe(text="Text to speak")
        async def speak(interaction: discord.Interaction, text: str):
            await self._handle_speak(interaction, text)

        @self._tree.command(name="config", description="Configure your personal TTS settings")
        @app_commands.describe(
            voz="Escolha a voz do TTS",
            idioma="Escolha o idioma (apenas para Mulher do Google)",
            sotaque="Escolha o sotaque (apenas para R.E.P.O.)",
        )
        @app_commands.choices(
            voz=[
                app_commands.Choice(name="Mulher do Google (melhor qualidade)", value="gtts"),
                app_commands.Choice(name="R.E.P.O. (robótico, mais rápido)", value="pyttsx3"),
            ]
        )
        @app_commands.choices(
            idioma=[
                app_commands.Choice(name="Português", value="pt"),
                app_commands.Choice(name="Inglês", value="en"),
                app_commands.Choice(name="Espanhol", value="es"),
                app_commands.Choice(name="Francês", value="fr"),
                app_commands.Choice(name="Alemão", value="de"),
                app_commands.Choice(name="Italiano", value="it"),
                app_commands.Choice(name="Japonês", value="ja"),
                app_commands.Choice(name="Coreano", value="ko"),
                app_commands.Choice(name="Chinês", value="zh"),
            ]
        )
        @app_commands.choices(
            sotaque=[
                app_commands.Choice(name="Português (Brasil)", value="roa/pt-br"),
                app_commands.Choice(name="Inglês (EUA)", value="en-us"),
                app_commands.Choice(name="Inglês (Reino Unido)", value="en-gb"),
                app_commands.Choice(name="Espanhol", value="roa/es"),
                app_commands.Choice(name="Francês", value="roa/fr"),
            ]
        )
        async def config(interaction: discord.Interaction, voz: str = None, idioma: str = None, sotaque: str = None):
            await self._handle_config(interaction, voz, idioma, sotaque)

        @self._tree.command(name="about", description="Show bot information and version")
        async def about(interaction: discord.Interaction):
            await self._handle_about(interaction)

    async def _send_bot_inactive_message(self, interaction: discord.Interaction) -> bool:
        try:
            await interaction.edit_original_response(
                content="❌ **Bot está desligando ou inativo!**\n\n"
                "🔄 Para reativar o bot, acesse:\n"
                "**https://python-tts-s3z8.onrender.com/**\n\n"
                "_(O servidor gratuito do Render desliga após inatividade)_"
            )
            return True
        except Exception as exc:
            logger.error("Failed to send bot inactive message: %s", exc)
            return False

    async def _handle_join(self, interaction: discord.Interaction):
        if not _has_voice_runtime_support():
            await interaction.response.send_message(_get_voice_dependency_message(), ephemeral=True)
            return

        guild_id = interaction.guild.id if interaction.guild else None
        member_id = interaction.user.id if interaction.user else None
        await interaction.response.defer(ephemeral=True)
        result = await self._join_use_case.execute(guild_id=guild_id, member_id=member_id)

        if result.code == "voice_connection_failed":
            error_msg = (result.error_detail or "").lower()
            if "interpreter shutdown" in error_msg or "cannot schedule new futures" in error_msg:
                await self._send_bot_inactive_message(interaction)
                return

        await interaction.edit_original_response(content=self._join_presenter.build_message(result))

    async def _handle_leave(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id if interaction.guild else None
        result = await self._leave_use_case.execute(guild_id=guild_id)
        await interaction.response.send_message(self._leave_presenter.build_message(result), ephemeral=True)

    async def _handle_speak(self, interaction: discord.Interaction, text: str):
        logger.info(
            "[SPEAK] Command from user %s (%s) in guild %s",
            interaction.user.id,
            interaction.user.name,
            interaction.guild.id if interaction.guild else "None",
        )
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not _has_voice_runtime_support():
            await interaction.edit_original_response(content=_get_voice_dependency_message())
            return

        try:
            if not interaction.guild or not interaction.guild.id:
                await interaction.edit_original_response(content="❌ Erro: Não foi possível determinar o servidor.")
                return

            tts_request = TTSRequest(text=text, guild_id=interaction.guild.id, member_id=interaction.user.id)
            result = await self._speak_use_case.execute(tts_request)

            try:
                if result.code == SPEAK_RESULT_QUEUED:
                    await interaction.edit_original_response(content=self._build_speak_message(result))
                elif result.code == SPEAK_RESULT_OK:
                    await interaction.delete_original_response()
                else:
                    await interaction.edit_original_response(content=self._build_speak_message(result))
            except discord.HTTPException as msg_error:
                logger.debug("[SPEAK] Could not update interaction message: %s", msg_error)
        except Exception as exc:
            logger.error("[SPEAK] Unexpected error: %s", exc, exc_info=True)
            try:
                error_msg = str(exc).lower()
                if "interpreter shutdown" in error_msg or "cannot schedule new futures" in error_msg:
                    await interaction.edit_original_response(content="❌ Bot está inativo ou desligando.")
                else:
                    await interaction.edit_original_response(content="❌ Erro inesperado")
            except Exception as send_error:
                logger.debug("[SPEAK] Could not send error message: %s", send_error)

    def _build_speak_message(self, result) -> str:
        return self._speak_presenter.build_message(result)

    async def _handle_config(self, interaction: discord.Interaction, voz: str | None, idioma: str | None, sotaque: str | None):
        if not interaction.guild or not interaction.guild.id:
            await interaction.response.send_message("❌ Este comando só pode ser usado em um servidor.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        logger.info(
            "[CONFIG] User %s in guild %s updating config: voz=%s, idioma=%s, sotaque=%s",
            interaction.user.id,
            guild_id,
            voz,
            idioma,
            sotaque,
        )

        if voz is None and idioma is None and sotaque is None:
            result = self._config_use_case.get_config(guild_id)
            if not result["success"]:
                await interaction.response.send_message(f"❌ {result['message']}", ephemeral=True)
                return

            config = result["config"]
            voz_nome = "Mulher do Google" if config["engine"] == "gtts" else "R.E.P.O. (robótico)"
            embed = discord.Embed(
                title="🎤 Configuração de Voz do Servidor",
                description=f"Configurações de {interaction.guild.name}",
                color=discord.Color.blue(),
            )
            embed.add_field(name="Voz", value=voz_nome, inline=True)
            embed.add_field(name="Idioma", value=config["language"].upper(), inline=True)
            embed.add_field(name="Sotaque", value=config["voice_id"], inline=True)
            embed.add_field(name="Taxa de Fala", value=str(config["rate"]), inline=True)
            embed.set_footer(text=f"Servidor (Guild ID: {guild_id})")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            result = await self._config_use_case.update_config_async(
                guild_id=guild_id,
                engine=voz,
                language=idioma,
                voice_id=sotaque,
            )
            if not result["success"]:
                await interaction.edit_original_response(content=f"❌ {result['message']}")
                return

            config = result["config"]
            voz_nome = "Mulher do Google" if config["engine"] == "gtts" else "R.E.P.O. (robótico)"
            embed = discord.Embed(
                title="✅ Configuração Atualizada",
                description=f"Configurações do servidor {interaction.guild.name} atualizadas",
                color=discord.Color.green(),
            )
            embed.add_field(name="Voz", value=voz_nome, inline=True)
            embed.add_field(name="Idioma", value=config["language"].upper(), inline=True)
            embed.add_field(name="Sotaque", value=config["voice_id"], inline=True)
            embed.set_footer(text=f"Servidor (Guild ID: {guild_id})")
            await interaction.edit_original_response(embed=embed)
        except Exception as exc:
            logger.error("[CONFIG] Error updating config for guild %s: %s", guild_id, exc, exc_info=True)
            await interaction.edit_original_response(content="❌ Erro ao atualizar configuração")

    async def _handle_about(self, interaction: discord.Interaction):
        from src.__version__ import __author__, __description__, __version__
        import platform

        embed = discord.Embed(title="🤖 TTS Bot Information", description=__description__, color=discord.Color.blue())
        embed.add_field(name="Version", value=f"`{__version__}`", inline=True)
        embed.add_field(name="Author", value=__author__, inline=True)
        embed.add_field(name="FFmpeg", value="✅ Available" if HAS_FFMPEG else "❌ Not found", inline=True)
        embed.add_field(name="PyNaCl", value="✅ Installed" if HAS_PYNACL else "❌ Not installed", inline=True)
        embed.add_field(name="davey", value="✅ Installed" if HAS_DAVEY else "❌ Not installed", inline=True)
        embed.add_field(
            name="Commands",
            value="• `/join` - Join your voice channel\n• `/leave` - Leave voice channel\n"
            "• `/speak` - Speak text\n• `/config` - Configure TTS settings\n• `/about` - Show this info",
            inline=False,
        )
        embed.set_footer(text=f"Running on {platform.system()} {platform.release()}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
