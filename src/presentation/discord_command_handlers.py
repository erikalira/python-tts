"""Focused handlers for Discord bot command flows."""

from __future__ import annotations

import logging
import platform

import discord

from src.application.results import ConfigureTTSResult
from src.application.voice_runtime import VoiceRuntimeStatus

logger = logging.getLogger(__name__)


class DiscordConfigCommandHandler:
    """Handle the `/config` command flow and embed construction."""

    def __init__(self, config_use_case):
        self._config_use_case = config_use_case

    async def handle(
        self,
        interaction: discord.Interaction,
        voz: str | None,
        idioma: str | None,
        sotaque: str | None,
    ) -> None:
        if not interaction.guild or not interaction.guild.id:
            await interaction.response.send_message("\u274c Este comando s\u00f3 pode ser usado em um servidor.", ephemeral=True)
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
            if not result.success:
                await interaction.response.send_message(f"\u274c {result.message}", ephemeral=True)
                return

            await interaction.response.send_message(
                embed=self._build_current_config_embed(interaction.guild.name, guild_id, result),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            result = await self._config_use_case.update_config_async(
                guild_id=guild_id,
                engine=voz,
                language=idioma,
                voice_id=sotaque,
            )
            if not result.success:
                await interaction.edit_original_response(content=f"\u274c {result.message}")
                return

            await interaction.edit_original_response(
                embed=self._build_updated_config_embed(interaction.guild.name, guild_id, result)
            )
        except Exception as exc:
            logger.error("[CONFIG] Error updating config for guild %s: %s", guild_id, exc, exc_info=True)
            await interaction.edit_original_response(content="\u274c Erro ao atualizar configura\u00e7\u00e3o")

    def _build_current_config_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
    ) -> discord.Embed:
        config = result.config
        voz_nome = "Mulher do Google" if config.engine == "gtts" else "R.E.P.O. (rob\u00f3tico)"
        embed = discord.Embed(
            title="\U0001f3a4 Configura\u00e7\u00e3o de Voz do Servidor",
            description=f"Configura\u00e7\u00f5es de {guild_name}",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Voz", value=voz_nome, inline=True)
        embed.add_field(name="Idioma", value=config.language.upper(), inline=True)
        embed.add_field(name="Sotaque", value=config.voice_id, inline=True)
        embed.add_field(name="Taxa de Fala", value=str(config.rate), inline=True)
        embed.set_footer(text=f"Servidor (Guild ID: {guild_id})")
        return embed

    def _build_updated_config_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
    ) -> discord.Embed:
        config = result.config
        voz_nome = "Mulher do Google" if config.engine == "gtts" else "R.E.P.O. (rob\u00f3tico)"
        embed = discord.Embed(
            title="\u2705 Configura\u00e7\u00e3o Atualizada",
            description=f"Configura\u00e7\u00f5es do servidor {guild_name} atualizadas",
            color=discord.Color.green(),
        )
        embed.add_field(name="Voz", value=voz_nome, inline=True)
        embed.add_field(name="Idioma", value=config.language.upper(), inline=True)
        embed.add_field(name="Sotaque", value=config.voice_id, inline=True)
        embed.set_footer(text=f"Servidor (Guild ID: {guild_id})")
        return embed


class DiscordAboutCommandHandler:
    """Build and send the `/about` response."""

    async def handle(
        self,
        interaction: discord.Interaction,
        runtime_status: VoiceRuntimeStatus,
    ) -> None:
        from src.__version__ import __author__, __description__, __version__

        embed = discord.Embed(
            title="\U0001f916 TTS Bot Information",
            description=__description__,
            color=discord.Color.blue(),
        )
        embed.add_field(name="Version", value=f"`{__version__}`", inline=True)
        embed.add_field(name="Author", value=__author__, inline=True)
        embed.add_field(name="FFmpeg", value="\u2705 Available" if runtime_status.ffmpeg_available else "\u274c Not found", inline=True)
        embed.add_field(name="PyNaCl", value="\u2705 Installed" if runtime_status.pynacl_installed else "\u274c Not installed", inline=True)
        embed.add_field(name="davey", value="\u2705 Installed" if runtime_status.davey_installed else "\u274c Not installed", inline=True)
        embed.add_field(
            name="Commands",
            value="\u2022 `/join` - Join your voice channel\n\u2022 `/leave` - Leave voice channel\n"
            "\u2022 `/speak` - Speak text\n\u2022 `/config` - Configure TTS settings\n\u2022 `/about` - Show this info",
            inline=False,
        )
        embed.set_footer(text=f"Running on {platform.system()} {platform.release()}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
