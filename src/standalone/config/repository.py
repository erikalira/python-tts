#!/usr/bin/env python3
"""Configuration persistence for the standalone application."""

import json
import os
from pathlib import Path
from typing import Optional

from .models import (
    DiscordConfig,
    HotkeyConfig,
    InterfaceConfig,
    NetworkConfig,
    StandaloneConfig,
    TTSConfig,
)
from .paths import get_config_directory


class ConfigurationRepository:
    """Repository for configuration persistence."""

    def __init__(self, config_file_path: Optional[Path] = None):
        if config_file_path:
            self._config_file = config_file_path
        else:
            self._config_file = get_config_directory() / "config.json"

    def load(self) -> StandaloneConfig:
        """Load configuration from file or create default."""
        if not self._config_file.exists():
            return StandaloneConfig.create_default()

        try:
            with open(self._config_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            return StandaloneConfig(
                tts=TTSConfig(
                    engine=os.getenv("TTS_ENGINE") or data.get("tts_engine", "gtts"),
                    language=os.getenv("TTS_LANGUAGE") or data.get("tts_language", "pt"),
                    voice_id=os.getenv("TTS_VOICE_ID") or data.get("tts_voice_id", "roa/pt-br"),
                    rate=int(os.getenv("TTS_RATE") or data.get("tts_rate", 180)),
                    output_device=os.getenv("TTS_OUTPUT_DEVICE") or data.get("tts_output_device"),
                ),
                discord=DiscordConfig(
                    bot_url=os.getenv("DISCORD_BOT_URL") or data.get("discord_bot_url"),
                    guild_id=os.getenv("DISCORD_GUILD_ID") or data.get("discord_guild_id"),
                    channel_id=os.getenv("DISCORD_CHANNEL_ID") or data.get("discord_channel_id"),
                    member_id=os.getenv("DISCORD_MEMBER_ID") or data.get("discord_member_id"),
                ),
                hotkey=HotkeyConfig(
                    trigger_open=data.get("trigger_open", "{"),
                    trigger_close=data.get("trigger_close", "}"),
                ),
                interface=InterfaceConfig(
                    show_notifications=data.get("show_notifications", True),
                    console_logs=data.get("console_logs", True),
                ),
                network=NetworkConfig(
                    request_timeout=data.get("request_timeout", 10),
                    user_agent=data.get("user_agent", "TTS-Hotkey/2.0"),
                    max_text_length=data.get("max_text_length", 500),
                ),
            )
        except Exception as exc:
            print(f"[CONFIG] ⚠️ Erro ao carregar configuração: {exc}")
            return StandaloneConfig.create_default()

    def save(self, config: StandaloneConfig) -> bool:
        """Save configuration to file."""
        try:
            data = {
                "tts_engine": config.tts.engine,
                "tts_language": config.tts.language,
                "tts_voice_id": config.tts.voice_id,
                "tts_rate": config.tts.rate,
                "tts_output_device": config.tts.output_device,
                "discord_bot_url": config.discord.bot_url,
                "discord_guild_id": config.discord.guild_id,
                "discord_channel_id": config.discord.channel_id,
                "discord_member_id": config.discord.member_id,
                "trigger_open": config.hotkey.trigger_open,
                "trigger_close": config.hotkey.trigger_close,
                "show_notifications": config.interface.show_notifications,
                "console_logs": config.interface.console_logs,
                "request_timeout": config.network.request_timeout,
                "user_agent": config.network.user_agent,
                "max_text_length": config.network.max_text_length,
            }

            with open(self._config_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=2, ensure_ascii=False)

            print(f"[CONFIG] ✅ Configuração salva em: {self._config_file}")
            return True
        except Exception as exc:
            print(f"[CONFIG] ❌ Erro ao salvar configuração: {exc}")
            return False
