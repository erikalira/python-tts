"""Discord bot commands."""

import logging

import discord
from discord import app_commands

from src.application.results import SPEAK_RESULT_OK, SPEAK_RESULT_QUEUED
from src.application.use_cases import (
    ConfigureTTSUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
    SpeakTextUseCase,
)
from src.application.voice_runtime import VoiceRuntimeAvailability, VoiceRuntimeStatus
from src.core.entities import TTSRequest
from src.presentation.discord_command_handlers import (
    DiscordAboutCommandHandler,
    DiscordConfigCommandHandler,
)
from src.presentation.discord_presenters import (
    DiscordJoinPresenter,
    DiscordLeavePresenter,
    DiscordSpeakPresenter,
)

logger = logging.getLogger(__name__)


def _get_voice_runtime_unavailable_message() -> str:
    return "\u274c O recurso de voz do bot est\u00e1 indispon\u00edvel no momento. Tente novamente mais tarde."


class DiscordCommands:
    """Discord slash commands handler."""

    def __init__(
        self,
        tree: app_commands.CommandTree,
        speak_use_case: SpeakTextUseCase,
        config_use_case: ConfigureTTSUseCase,
        join_use_case: JoinVoiceChannelUseCase,
        leave_use_case: LeaveVoiceChannelUseCase,
        voice_runtime_availability: VoiceRuntimeAvailability,
    ):
        self._tree = tree
        self._speak_use_case = speak_use_case
        self._config_use_case = config_use_case
        self._join_use_case = join_use_case
        self._leave_use_case = leave_use_case
        self._voice_runtime_availability = voice_runtime_availability
        self._join_presenter = DiscordJoinPresenter()
        self._leave_presenter = DiscordLeavePresenter()
        self._speak_presenter = DiscordSpeakPresenter()
        self._config_handler = DiscordConfigCommandHandler(config_use_case)
        self._about_handler = DiscordAboutCommandHandler()
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
                app_commands.Choice(name="R.E.P.O. (rob\u00f3tico, mais r\u00e1pido)", value="pyttsx3"),
            ]
        )
        @app_commands.choices(
            idioma=[
                app_commands.Choice(name="Portugu\u00eas", value="pt"),
                app_commands.Choice(name="Ingl\u00eas", value="en"),
                app_commands.Choice(name="Espanhol", value="es"),
                app_commands.Choice(name="Franc\u00eas", value="fr"),
                app_commands.Choice(name="Alem\u00e3o", value="de"),
                app_commands.Choice(name="Italiano", value="it"),
                app_commands.Choice(name="Japon\u00eas", value="ja"),
                app_commands.Choice(name="Coreano", value="ko"),
                app_commands.Choice(name="Chin\u00eas", value="zh"),
            ]
        )
        @app_commands.choices(
            sotaque=[
                app_commands.Choice(name="Portugu\u00eas (Brasil)", value="roa/pt-br"),
                app_commands.Choice(name="Ingl\u00eas (EUA)", value="en-us"),
                app_commands.Choice(name="Ingl\u00eas (Reino Unido)", value="en-gb"),
                app_commands.Choice(name="Espanhol", value="roa/es"),
                app_commands.Choice(name="Franc\u00eas", value="roa/fr"),
            ]
        )
        async def config(interaction: discord.Interaction, voz: str = None, idioma: str = None, sotaque: str = None):
            await self._handle_config(interaction, voz, idioma, sotaque)

        @self._tree.command(name="about", description="Show bot information and version")
        async def about(interaction: discord.Interaction):
            await self._handle_about(interaction)

    def _get_voice_runtime_status(self) -> VoiceRuntimeStatus:
        return self._voice_runtime_availability.get_status()

    def _log_voice_runtime_unavailable(self, command_name: str) -> None:
        missing = self._get_voice_runtime_status().missing_dependencies()
        logger.error(
            "[VOICE_RUNTIME] Command '%s' blocked because required server dependencies are missing: %s",
            command_name,
            ", ".join(missing) if missing else "unknown",
        )

    async def _send_bot_inactive_message(self, interaction: discord.Interaction) -> bool:
        try:
            await interaction.edit_original_response(
                content="\u274c **Bot est\u00e1 desligando ou inativo!**\n\n"
                "\U0001f504 Para reativar o bot, acesse:\n"
                "**https://python-tts-s3z8.onrender.com/**\n\n"
                "_(O servidor gratuito do Render desliga ap\u00f3s inatividade)_"
            )
            return True
        except Exception as exc:
            logger.error("Failed to send bot inactive message: %s", exc)
            return False

    async def _handle_join(self, interaction: discord.Interaction):
        if not self._get_voice_runtime_status().is_available:
            self._log_voice_runtime_unavailable("join")
            await interaction.response.send_message(_get_voice_runtime_unavailable_message(), ephemeral=True)
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

        if not self._get_voice_runtime_status().is_available:
            self._log_voice_runtime_unavailable("speak")
            await interaction.edit_original_response(content=_get_voice_runtime_unavailable_message())
            return

        try:
            if not interaction.guild or not interaction.guild.id:
                await interaction.edit_original_response(content="\u274c Erro: N\u00e3o foi poss\u00edvel determinar o servidor.")
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
                    await interaction.edit_original_response(content="\u274c Bot est\u00e1 inativo ou desligando.")
                else:
                    await interaction.edit_original_response(content="\u274c Erro inesperado")
            except Exception as send_error:
                logger.debug("[SPEAK] Could not send error message: %s", send_error)

    def _build_speak_message(self, result) -> str:
        return self._speak_presenter.build_message(result)

    async def _handle_config(self, interaction: discord.Interaction, voz: str | None, idioma: str | None, sotaque: str | None):
        await self._config_handler.handle(interaction, voz, idioma, sotaque)

    async def _handle_about(self, interaction: discord.Interaction):
        await self._about_handler.handle(interaction, self._get_voice_runtime_status())
