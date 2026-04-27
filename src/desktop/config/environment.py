#!/usr/bin/env python3
"""Environment synchronization for Desktop App configuration."""

import logging
import os

from .models import DesktopAppConfig

logger = logging.getLogger(__name__)


class EnvironmentUpdater:
    """Updates environment variables from configuration."""

    @staticmethod
    def update_from_config(config: DesktopAppConfig) -> None:
        """Update environment variables from configuration."""
        os.environ["DISCORD_BOT_URL"] = config.discord.bot_url

        if config.discord.member_id:
            os.environ["DISCORD_MEMBER_ID"] = config.discord.member_id
        else:
            os.environ.pop("DISCORD_MEMBER_ID", None)

        if config.discord.speak_token:
            os.environ["BOT_SPEAK_TOKEN"] = config.discord.speak_token
        else:
            os.environ.pop("BOT_SPEAK_TOKEN", None)

        os.environ["TTS_ENGINE"] = config.tts.engine
        os.environ["TTS_LANGUAGE"] = config.tts.language
        os.environ["TTS_VOICE_ID"] = config.tts.voice_id

        if config.tts.output_device:
            os.environ["TTS_OUTPUT_DEVICE"] = config.tts.output_device

        logger.info(
            "[CONFIG] Environment variables updated - DISCORD_MEMBER_ID: %s",
            config.discord.member_id,
        )
