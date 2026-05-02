"""Focused handlers for Discord bot command flows."""

from __future__ import annotations

import logging
import platform

import discord

from src.application.dto import ConfigureTTSResult, TTSConfigurationData
from src.application.tts_config_use_case import ConfigureTTSUseCase
from src.application.tts_voice_catalog import TTSCatalog
from src.application.voice_runtime import VoiceRuntimeStatus
from src.presentation.discord_i18n import DEFAULT_LOCALE, DiscordMessageCatalog

logger = logging.getLogger(__name__)


class _BaseConfigEmbedBuilder:
    def __init__(self, tts_catalog: TTSCatalog) -> None:
        self._tts_catalog = tts_catalog
        self._messages = DiscordMessageCatalog()

    def _resolve_voice_name(self, config: TTSConfigurationData) -> str:
        resolved_voice = self._tts_catalog.find_voice_option(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
        )
        return (
            resolved_voice.label if resolved_voice else self._build_fallback_voice_label(config.engine, config.voice_id)
        )

    def _build_fallback_voice_label(self, engine: str, voice_id: str) -> str:
        if engine == "gtts":
            return f"Google TTS - {voice_id}"
        if engine == "edge-tts":
            return f"Edge TTS - {voice_id}"
        return f"R.E.P.O. - {voice_id}"

    def _add_voice_resolution_field(self, embed: discord.Embed, engine: str, voice_id: str, locale: str) -> None:
        if engine == "gtts":
            embed.add_field(
                name=self._messages.text("voice_resolution.name", locale),
                value=self._messages.text("voice_resolution.gtts", locale),
                inline=False,
            )
            return

        if engine == "edge-tts":
            embed.add_field(
                name=self._messages.text("voice_resolution.name", locale),
                value=self._messages.text("voice_resolution.edge", locale, voice_id=voice_id),
                inline=False,
            )
            return

        if self._tts_catalog.is_voice_available(engine=engine, voice_id=voice_id):
            message = self._messages.text("voice_resolution.pyttsx3.found", locale, voice_id=voice_id)
        else:
            message = self._messages.text("voice_resolution.pyttsx3.missing", locale, voice_id=voice_id)
        embed.add_field(name=self._messages.text("voice_resolution.name", locale), value=message, inline=False)

    def _scope_label(self, scope: str | None, locale: str) -> str:
        if scope == "user":
            return self._messages.text("config.scope.user", locale)
        if scope == "guild":
            return self._messages.text("config.scope.guild", locale)
        return self._messages.text("config.scope.global", locale)

    def _require_config(self, result: ConfigureTTSResult) -> TTSConfigurationData:
        if result.config is None:
            raise ValueError("ConfigureTTSResult.config is required for config embeds")
        return result.config


class DiscordConfigCommandHandler(_BaseConfigEmbedBuilder):
    """Handle the `/config` command flow and embed construction."""

    def __init__(self, config_use_case: ConfigureTTSUseCase, tts_catalog: TTSCatalog) -> None:
        super().__init__(tts_catalog)
        self._config_use_case = config_use_case

    async def handle(
        self,
        interaction: discord.Interaction,
        voice: str | None,
        locale: str,
    ) -> None:
        if not interaction.guild or not interaction.guild.id:
            await interaction.response.send_message(self._messages.text("error.guild_only", locale), ephemeral=True)
            return

        guild_id = interaction.guild.id
        user_id = interaction.user.id if interaction.user else None
        logger.info(
            "[CONFIG] User %s in guild %s updating personal config: voice=%s",
            interaction.user.id,
            guild_id,
            voice,
        )

        if voice is None:
            result = self._config_use_case.get_config(guild_id, user_id=user_id)
            if not result.success:
                await interaction.response.send_message(f"❌ {result.message}", ephemeral=True)
                return

            await interaction.response.send_message(
                embed=self._build_current_config_embed(interaction.guild.name, guild_id, result, locale),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            selected_voice = self._tts_catalog.get_voice_option(voice)
            if selected_voice is None:
                await interaction.edit_original_response(content=self._messages.text("error.invalid_voice", locale))
                return

            result = await self._config_use_case.update_config_async(
                guild_id=guild_id,
                user_id=user_id,
                engine=selected_voice.engine,
                language=selected_voice.language,
                voice_id=selected_voice.voice_id,
            )
            if not result.success:
                await interaction.edit_original_response(content=f"❌ {result.message}")
                return

            await interaction.edit_original_response(
                embed=self._build_updated_config_embed(interaction.guild.name, guild_id, result, locale)
            )
        except Exception as exc:
            logger.error("[CONFIG] Error updating config for guild %s: %s", guild_id, exc, exc_info=True)
            await interaction.edit_original_response(content=self._messages.text("config.update_error", locale))

    async def handle_reset(self, interaction: discord.Interaction, locale: str) -> None:
        if not interaction.guild or not interaction.guild.id:
            await interaction.response.send_message(self._messages.text("error.guild_only", locale), ephemeral=True)
            return

        guild_id = interaction.guild.id
        user_id = interaction.user.id if interaction.user else None
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            result = await self._config_use_case.reset_config_async(guild_id, user_id=user_id)
            if not result.success:
                await interaction.edit_original_response(content=f"❌ {result.message}")
                return
            await interaction.edit_original_response(
                embed=self._build_reset_config_embed(interaction.guild.name, guild_id, result, locale)
            )
        except Exception as exc:
            logger.error("[CONFIG] Error resetting personal config for guild %s: %s", guild_id, exc, exc_info=True)
            await interaction.edit_original_response(content=self._messages.text("config.reset_error", locale))

    def _build_current_config_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
        locale: str = DEFAULT_LOCALE,
    ) -> discord.Embed:
        config = self._require_config(result)
        voice_name = self._resolve_voice_name(config)
        embed = discord.Embed(
            title=self._messages.text("config.title.current", locale),
            description=self._messages.text("config.description.current", locale, guild_name=guild_name),
            color=discord.Color.blue(),
        )
        embed.add_field(name=self._messages.text("config.field.voice", locale), value=voice_name, inline=True)
        embed.add_field(name=self._messages.text("config.field.rate", locale), value=str(config.rate), inline=True)
        embed.add_field(
            name=self._messages.text("config.field.scope", locale),
            value=self._messages.text("config.scope.personal", locale),
            inline=False,
        )
        embed.add_field(
            name=self._messages.text("config.field.effective_source", locale),
            value=self._scope_label(result.scope, locale),
            inline=False,
        )
        self._add_voice_resolution_field(embed, config.engine, config.voice_id, locale)
        embed.set_footer(text=self._messages.text("config.footer.guild", locale, guild_id=guild_id))
        return embed

    def _build_updated_config_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
        locale: str = DEFAULT_LOCALE,
    ) -> discord.Embed:
        config = self._require_config(result)
        voice_name = self._resolve_voice_name(config)
        embed = discord.Embed(
            title=self._messages.text("config.title.updated", locale),
            description=self._messages.text("config.description.updated", locale, guild_name=guild_name),
            color=discord.Color.green(),
        )
        embed.add_field(name=self._messages.text("config.field.voice", locale), value=voice_name, inline=True)
        embed.add_field(
            name=self._messages.text("config.field.scope", locale),
            value=self._messages.text("config.scope.saved", locale),
            inline=False,
        )
        embed.add_field(
            name=self._messages.text("config.field.effective_source", locale),
            value=self._scope_label(result.scope, locale),
            inline=False,
        )
        self._add_voice_resolution_field(embed, config.engine, config.voice_id, locale)
        embed.set_footer(text=self._messages.text("config.footer.guild", locale, guild_id=guild_id))
        return embed

    def _build_reset_config_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
        locale: str = DEFAULT_LOCALE,
    ) -> discord.Embed:
        config = self._require_config(result)
        voice_name = self._resolve_voice_name(config)
        embed = discord.Embed(
            title=self._messages.text("config.title.reset", locale),
            description=self._messages.text("config.description.reset", locale, guild_name=guild_name),
            color=discord.Color.orange(),
        )
        embed.add_field(name=self._messages.text("config.field.active_voice", locale), value=voice_name, inline=True)
        embed.add_field(
            name=self._messages.text("config.field.effective_source", locale),
            value=self._scope_label(result.scope, locale),
            inline=False,
        )
        self._add_voice_resolution_field(embed, config.engine, config.voice_id, locale)
        embed.set_footer(text=self._messages.text("config.footer.guild", locale, guild_id=guild_id))
        return embed


class DiscordServerConfigCommandHandler(_BaseConfigEmbedBuilder):
    """Handle the `/server-config` command flow for guild defaults."""

    def __init__(self, config_use_case: ConfigureTTSUseCase, tts_catalog: TTSCatalog) -> None:
        super().__init__(tts_catalog)
        self._config_use_case = config_use_case

    async def handle(
        self,
        interaction: discord.Interaction,
        voice: str | None,
        locale: str,
    ) -> None:
        if not interaction.guild or not interaction.guild.id:
            await interaction.response.send_message(self._messages.text("error.guild_only", locale), ephemeral=True)
            return

        if not self._can_manage_guild(interaction):
            await interaction.response.send_message(
                self._messages.text("server_config.permission.update", locale),
                ephemeral=True,
            )
            return

        guild_id = interaction.guild.id

        if voice is None:
            result = self._config_use_case.get_config(guild_id)
            if not result.success:
                await interaction.response.send_message(f"❌ {result.message}", ephemeral=True)
                return

            await interaction.response.send_message(
                embed=self._build_server_config_embed(interaction.guild.name, guild_id, result, locale),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            selected_voice = self._tts_catalog.get_voice_option(voice)
            if selected_voice is None:
                await interaction.edit_original_response(content=self._messages.text("error.invalid_voice", locale))
                return

            result = await self._config_use_case.update_config_async(
                guild_id=guild_id,
                engine=selected_voice.engine,
                language=selected_voice.language,
                voice_id=selected_voice.voice_id,
            )
            if not result.success:
                await interaction.edit_original_response(content=f"❌ {result.message}")
                return

            await interaction.edit_original_response(
                embed=self._build_server_config_updated_embed(interaction.guild.name, guild_id, result, locale)
            )
        except Exception as exc:
            logger.error("[SERVER_CONFIG] Error updating config for guild %s: %s", guild_id, exc, exc_info=True)
            await interaction.edit_original_response(content=self._messages.text("server_config.update_error", locale))

    async def handle_reset(self, interaction: discord.Interaction, locale: str) -> None:
        if not interaction.guild or not interaction.guild.id:
            await interaction.response.send_message(self._messages.text("error.guild_only", locale), ephemeral=True)
            return

        if not self._can_manage_guild(interaction):
            await interaction.response.send_message(
                self._messages.text("server_config.permission.reset", locale),
                ephemeral=True,
            )
            return

        guild_id = interaction.guild.id
        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            result = await self._config_use_case.reset_config_async(guild_id)
            if not result.success:
                await interaction.edit_original_response(content=f"❌ {result.message}")
                return
            await interaction.edit_original_response(
                embed=self._build_server_reset_embed(interaction.guild.name, guild_id, result, locale)
            )
        except Exception as exc:
            logger.error("[SERVER_CONFIG] Error resetting config for guild %s: %s", guild_id, exc, exc_info=True)
            await interaction.edit_original_response(content=self._messages.text("server_config.reset_error", locale))

    def _can_manage_guild(self, interaction: discord.Interaction) -> bool:
        permissions = getattr(getattr(interaction, "user", None), "guild_permissions", None)
        return bool(getattr(permissions, "manage_guild", False))

    def _build_server_config_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
        locale: str = DEFAULT_LOCALE,
    ) -> discord.Embed:
        config = self._require_config(result)
        voice_name = self._resolve_voice_name(config)
        embed = discord.Embed(
            title=self._messages.text("server_config.title.current", locale),
            description=self._messages.text("server_config.description.current", locale, guild_name=guild_name),
            color=discord.Color.blurple(),
        )
        embed.add_field(name=self._messages.text("config.field.voice", locale), value=voice_name, inline=True)
        embed.add_field(name=self._messages.text("config.field.rate", locale), value=str(config.rate), inline=True)
        embed.add_field(
            name=self._messages.text("config.field.scope", locale),
            value=self._messages.text("config.scope.guild", locale),
            inline=False,
        )
        embed.add_field(
            name=self._messages.text("config.field.effective_source", locale),
            value=self._scope_label(result.scope, locale),
            inline=False,
        )
        self._add_voice_resolution_field(embed, config.engine, config.voice_id, locale)
        embed.set_footer(text=self._messages.text("config.footer.guild", locale, guild_id=guild_id))
        return embed

    def _build_server_config_updated_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
        locale: str = DEFAULT_LOCALE,
    ) -> discord.Embed:
        config = self._require_config(result)
        voice_name = self._resolve_voice_name(config)
        embed = discord.Embed(
            title=self._messages.text("server_config.title.updated", locale),
            description=self._messages.text("server_config.description.updated", locale, guild_name=guild_name),
            color=discord.Color.green(),
        )
        embed.add_field(name=self._messages.text("config.field.voice", locale), value=voice_name, inline=True)
        embed.add_field(
            name=self._messages.text("config.field.scope", locale),
            value=self._messages.text("server_config.scope.saved", locale),
            inline=False,
        )
        embed.add_field(
            name=self._messages.text("config.field.effective_source", locale),
            value=self._scope_label(result.scope, locale),
            inline=False,
        )
        self._add_voice_resolution_field(embed, config.engine, config.voice_id, locale)
        embed.set_footer(text=self._messages.text("config.footer.guild", locale, guild_id=guild_id))
        return embed

    def _build_server_reset_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
        locale: str = DEFAULT_LOCALE,
    ) -> discord.Embed:
        config = self._require_config(result)
        voice_name = self._resolve_voice_name(config)
        embed = discord.Embed(
            title=self._messages.text("server_config.title.reset", locale),
            description=self._messages.text("server_config.description.reset", locale, guild_name=guild_name),
            color=discord.Color.orange(),
        )
        embed.add_field(name=self._messages.text("config.field.active_voice", locale), value=voice_name, inline=True)
        embed.add_field(
            name=self._messages.text("config.field.effective_source", locale),
            value=self._scope_label(result.scope, locale),
            inline=False,
        )
        self._add_voice_resolution_field(embed, config.engine, config.voice_id, locale)
        embed.set_footer(text=self._messages.text("config.footer.guild", locale, guild_id=guild_id))
        return embed


class DiscordAboutCommandHandler:
    """Build and send the `/about` response."""

    def __init__(self) -> None:
        self._messages = DiscordMessageCatalog()

    async def handle(
        self,
        interaction: discord.Interaction,
        runtime_status: VoiceRuntimeStatus,
        locale: str,
    ) -> None:
        from src.__version__ import __author__, __description__, __version__

        embed = discord.Embed(
            title=self._messages.text("about.title", locale),
            description=__description__,
            color=discord.Color.blue(),
        )
        embed.add_field(name=self._messages.text("about.version", locale), value=f"`{__version__}`", inline=True)
        embed.add_field(name=self._messages.text("about.author", locale), value=__author__, inline=True)
        embed.add_field(
            name="FFmpeg",
            value=self._messages.text(
                "about.available" if runtime_status.ffmpeg_available else "about.not_found", locale
            ),
            inline=True,
        )
        embed.add_field(
            name="PyNaCl",
            value=self._messages.text(
                "about.installed" if runtime_status.pynacl_installed else "about.not_installed", locale
            ),
            inline=True,
        )
        embed.add_field(
            name="davey",
            value=self._messages.text(
                "about.installed" if runtime_status.davey_installed else "about.not_installed", locale
            ),
            inline=True,
        )
        embed.add_field(
            name=self._messages.text("about.commands", locale),
            value=self._messages.text("about.commands.value", locale),
            inline=False,
        )
        embed.set_footer(
            text=self._messages.text("about.footer", locale, system=platform.system(), release=platform.release())
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
