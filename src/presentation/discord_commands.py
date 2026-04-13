"""Discord bot commands."""

import logging

import discord
from discord import app_commands

from src.application.discord_speak_request_builder import DiscordSpeakRequestBuilder
from src.application.dto import SPEAK_RESULT_OK, SPEAK_RESULT_QUEUED
from src.application.tts_voice_catalog import TTSCatalog
from src.application.use_cases import (
    ConfigureTTSUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
    SpeakTextUseCase,
)
from src.application.voice_runtime import VoiceRuntimeAvailability, VoiceRuntimeStatus
from src.presentation.discord_command_handlers import (
    DiscordAboutCommandHandler,
    DiscordConfigCommandHandler,
    DiscordServerConfigCommandHandler,
)
from src.presentation.discord_presenters import (
    DiscordJoinPresenter,
    DiscordLeavePresenter,
    DiscordSpeakPresenter,
)

logger = logging.getLogger(__name__)


def _get_voice_runtime_unavailable_message() -> str:
    return "❌ O recurso de voz do bot está indisponível no momento. Tente novamente mais tarde."


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
        tts_catalog: TTSCatalog,
    ):
        self._tree = tree
        self._speak_use_case = speak_use_case
        self._config_use_case = config_use_case
        self._join_use_case = join_use_case
        self._leave_use_case = leave_use_case
        self._voice_runtime_availability = voice_runtime_availability
        self._tts_catalog = tts_catalog
        self._join_presenter = DiscordJoinPresenter()
        self._leave_presenter = DiscordLeavePresenter()
        self._speak_presenter = DiscordSpeakPresenter()
        self._config_handler = DiscordConfigCommandHandler(config_use_case, tts_catalog)
        self._server_config_handler = DiscordServerConfigCommandHandler(config_use_case, tts_catalog)
        self._about_handler = DiscordAboutCommandHandler()
        self._speak_request_builder = DiscordSpeakRequestBuilder(config_use_case, tts_catalog)
        self._register_commands()

    def _register_commands(self):
        @self._tree.command(name="join", description="Make the bot join your voice channel")
        async def join(interaction: discord.Interaction):
            await self._handle_join(interaction)

        @self._tree.command(name="leave", description="Make the bot leave the voice channel")
        async def leave(interaction: discord.Interaction):
            await self._handle_leave(interaction)

        @self._tree.command(name="speak", description="Make the bot speak the given text in voice channel")
        @app_commands.describe(text="Text to speak", voz="Escolha uma voz apenas para esta fala")
        @app_commands.autocomplete(voz=self._autocomplete_voz)
        async def speak(interaction: discord.Interaction, text: str, voz: str = None):
            await self._handle_speak(interaction, text, voz)

        @self._tree.command(name="config", description="Configure your personal TTS settings")
        @app_commands.describe(voz="Escolha a voz completa que o bot deve usar")
        @app_commands.autocomplete(voz=self._autocomplete_voz)
        async def config(interaction: discord.Interaction, voz: str = None):
            await self._handle_config(interaction, voz)

        @self._tree.command(name="config-reset", description="Reset your personal voice override")
        async def config_reset(interaction: discord.Interaction):
            await self._handle_config_reset(interaction)

        @self._tree.command(name="server-config", description="Configure the default server voice")
        @app_commands.describe(voz="Escolha a voz padrão para usuários sem configuração pessoal")
        @app_commands.autocomplete(voz=self._autocomplete_voz)
        async def server_config(interaction: discord.Interaction, voz: str = None):
            await self._handle_server_config(interaction, voz)

        @self._tree.command(name="server-config-reset", description="Reset the default server voice")
        async def server_config_reset(interaction: discord.Interaction):
            await self._handle_server_config_reset(interaction)

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

    async def _handle_speak(self, interaction: discord.Interaction, text: str, voz: str | None = None):
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
            prepared_request = self._speak_request_builder.build(
                text=text,
                guild_id=interaction.guild.id if interaction.guild else None,
                member_id=interaction.user.id if interaction.user else None,
                voice_key=voz,
            )
            if prepared_request.error_message:
                await interaction.edit_original_response(content=prepared_request.error_message)
                return

            result = await self._speak_use_case.execute(prepared_request.request)

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

    async def _handle_config(self, interaction: discord.Interaction, voz: str | None):
        await self._config_handler.handle(interaction, voz)

    async def _handle_config_reset(self, interaction: discord.Interaction):
        await self._config_handler.handle_reset(interaction)

    async def _handle_server_config(self, interaction: discord.Interaction, voz: str | None):
        await self._server_config_handler.handle(interaction, voz)

    async def _handle_server_config_reset(self, interaction: discord.Interaction):
        await self._server_config_handler.handle_reset(interaction)

    async def _handle_about(self, interaction: discord.Interaction):
        await self._about_handler.handle(interaction, self._get_voice_runtime_status())

    async def _autocomplete_voz(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        options = self._tts_catalog.list_voice_options()
        current_normalized = current.lower().strip()

        if current_normalized:
            options = [
                option
                for option in options
                if current_normalized in option.label.lower()
                or current_normalized in option.voice_id.lower()
                or current_normalized in option.key.lower()
            ]

        return [
            app_commands.Choice(name=option.label, value=option.key)
            for option in options[:25]
        ]
