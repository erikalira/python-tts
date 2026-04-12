"""Focused handlers for Discord bot command flows."""

from __future__ import annotations

import logging
import platform

import discord

from src.application.dto import ConfigureTTSResult
from src.application.tts_voice_catalog import TTSCatalog
from src.application.voice_runtime import VoiceRuntimeStatus

logger = logging.getLogger(__name__)


class DiscordConfigCommandHandler:
    """Handle the `/config` command flow and embed construction."""

    def __init__(self, config_use_case, tts_catalog: TTSCatalog):
        self._config_use_case = config_use_case
        self._tts_catalog = tts_catalog

    async def handle(
        self,
        interaction: discord.Interaction,
        voz: str | None,
    ) -> None:
        if not interaction.guild or not interaction.guild.id:
            await interaction.response.send_message("❌ Este comando só pode ser usado em um servidor.", ephemeral=True)
            return

        guild_id = interaction.guild.id
        logger.info(
            "[CONFIG] User %s in guild %s updating config: voz=%s",
            interaction.user.id,
            guild_id,
            voz,
        )

        if voz is None:
            result = self._config_use_case.get_config(guild_id)
            if not result.success:
                await interaction.response.send_message(f"❌ {result.message}", ephemeral=True)
                return

            await interaction.response.send_message(
                embed=self._build_current_config_embed(interaction.guild.name, guild_id, result),
                ephemeral=True,
            )
            return

        await interaction.response.defer(ephemeral=True, thinking=True)
        try:
            selected_voice = self._tts_catalog.get_voice_option(voz)
            if selected_voice is None:
                await interaction.edit_original_response(content="❌ Voz inválida ou indisponível.")
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
                embed=self._build_updated_config_embed(interaction.guild.name, guild_id, result)
            )
        except Exception as exc:
            logger.error("[CONFIG] Error updating config for guild %s: %s", guild_id, exc, exc_info=True)
            await interaction.edit_original_response(content="❌ Erro ao atualizar configuração")

    def _build_current_config_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
    ) -> discord.Embed:
        config = result.config
        resolved_voice = self._tts_catalog.find_voice_option(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
        )
        voz_nome = resolved_voice.label if resolved_voice else self._build_fallback_voice_label(config.engine, config.voice_id)
        embed = discord.Embed(
            title="🎤 Configuração de Voz do Servidor",
            description=f"Configurações de {guild_name}",
            color=discord.Color.blue(),
        )
        embed.add_field(name="Voz", value=voz_nome, inline=True)
        embed.add_field(name="Taxa de Fala", value=str(config.rate), inline=True)
        self._add_voice_resolution_field(embed, config.engine, config.voice_id)
        embed.set_footer(text=f"Servidor (Guild ID: {guild_id})")
        return embed

    def _build_updated_config_embed(
        self,
        guild_name: str,
        guild_id: int,
        result: ConfigureTTSResult,
    ) -> discord.Embed:
        config = result.config
        resolved_voice = self._tts_catalog.find_voice_option(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
        )
        voz_nome = resolved_voice.label if resolved_voice else self._build_fallback_voice_label(config.engine, config.voice_id)
        embed = discord.Embed(
            title="✅ Configuração Atualizada",
            description=f"Configurações do servidor {guild_name} atualizadas",
            color=discord.Color.green(),
        )
        embed.add_field(name="Voz", value=voz_nome, inline=True)
        self._add_voice_resolution_field(embed, config.engine, config.voice_id)
        embed.set_footer(text=f"Servidor (Guild ID: {guild_id})")
        return embed

    def _build_fallback_voice_label(self, engine: str, voice_id: str) -> str:
        if engine == "gtts":
            return f"Google TTS - {voice_id}"
        if engine == "edge-tts":
            return f"Edge TTS - {voice_id}"
        return f"R.E.P.O. - {voice_id}"

    def _add_voice_resolution_field(self, embed: discord.Embed, engine: str, voice_id: str) -> None:
        if engine == "gtts":
            embed.add_field(
                name="Resolução da Voz",
                value="Google TTS usa o idioma selecionado; não há catálogo local de vozes do sistema.",
                inline=False,
            )
            return

        if engine == "edge-tts":
            embed.add_field(
                name="Resolução da Voz",
                value=f"Edge TTS usará a voz neural '{voice_id}'.",
                inline=False,
            )
            return

        if self._tts_catalog.is_voice_available(engine=engine, voice_id=voice_id):
            message = f"Voz do Windows encontrada para '{voice_id}'."
        else:
            message = f"Voice ID '{voice_id}' não encontrado; o pyttsx3 usará a voz padrão do Windows."
        embed.add_field(name="Resolução da Voz", value=message, inline=False)


class DiscordAboutCommandHandler:
    """Build and send the `/about` response."""

    async def handle(
        self,
        interaction: discord.Interaction,
        runtime_status: VoiceRuntimeStatus,
    ) -> None:
        from src.__version__ import __author__, __description__, __version__

        embed = discord.Embed(
            title="🤖 TTS Bot Information",
            description=__description__,
            color=discord.Color.blue(),
        )
        embed.add_field(name="Version", value=f"`{__version__}`", inline=True)
        embed.add_field(name="Author", value=__author__, inline=True)
        embed.add_field(name="FFmpeg", value="✅ Available" if runtime_status.ffmpeg_available else "❌ Not found", inline=True)
        embed.add_field(name="PyNaCl", value="✅ Installed" if runtime_status.pynacl_installed else "❌ Not installed", inline=True)
        embed.add_field(name="davey", value="✅ Installed" if runtime_status.davey_installed else "❌ Not installed", inline=True)
        embed.add_field(
            name="Commands",
            value="• `/join` - Join your voice channel\n• `/leave` - Leave voice channel\n"
            "• `/speak` - Speak text\n• `/config` - Configure TTS settings\n• `/about` - Show this info",
            inline=False,
        )
        embed.set_footer(text=f"Running on {platform.system()} {platform.release()}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
