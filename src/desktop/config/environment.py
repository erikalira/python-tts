#!/usr/bin/env python3
"""Environment synchronization for Desktop App configuration."""

import os

from .models import DesktopAppConfig


class EnvironmentUpdater:
    """Updates environment variables from configuration."""

    @staticmethod
    def update_from_config(config: DesktopAppConfig) -> None:
        """Update environment variables from configuration."""
        os.environ["DISCORD_BOT_URL"] = config.discord.bot_url

        if config.discord.guild_id:
            os.environ["DISCORD_GUILD_ID"] = config.discord.guild_id
        else:
            os.environ.pop("DISCORD_GUILD_ID", None)

        if config.discord.channel_id:
            os.environ["DISCORD_CHANNEL_ID"] = config.discord.channel_id
        else:
            os.environ.pop("DISCORD_CHANNEL_ID", None)

        if config.discord.member_id:
            os.environ["DISCORD_MEMBER_ID"] = config.discord.member_id
        else:
            os.environ.pop("DISCORD_MEMBER_ID", None)

        os.environ["TTS_ENGINE"] = config.tts.engine
        os.environ["TTS_LANGUAGE"] = config.tts.language
        os.environ["TTS_VOICE_ID"] = config.tts.voice_id

        if config.tts.output_device:
            os.environ["TTS_OUTPUT_DEVICE"] = config.tts.output_device

        print(
            "[CONFIG] ✅ Variáveis de ambiente atualizadas - "
            f"DISCORD_GUILD_ID: {config.discord.guild_id}, "
            f"DISCORD_MEMBER_ID: {config.discord.member_id}"
        )
