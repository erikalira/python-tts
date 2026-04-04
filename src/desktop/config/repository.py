#!/usr/bin/env python3
"""Configuration persistence for the Desktop App."""

import json
import os
from pathlib import Path
from typing import Optional

from .models import (
    DiscordConfig,
    HotkeyConfig,
    InterfaceConfig,
    NetworkConfig,
    DesktopAppConfig,
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

    def load(self) -> DesktopAppConfig:
        """Load configuration from file or create default."""
        if not self._config_file.exists():
            return DesktopAppConfig.create_default()

        try:
            with open(self._config_file, "r", encoding="utf-8") as file:
                data = json.load(file)

            return DesktopAppConfig(
                tts=TTSConfig(
                    engine=self._get_env_or_file_value(data, "tts_engine", "TTS_ENGINE", "gtts"),
                    language=self._get_env_or_file_value(data, "tts_language", "TTS_LANGUAGE", "pt"),
                    voice_id=self._get_env_or_file_value(data, "tts_voice_id", "TTS_VOICE_ID", "roa/pt-br"),
                    rate=int(self._get_env_or_file_value(data, "tts_rate", "TTS_RATE", 180)),
                    output_device=self._get_env_or_file_value(data, "tts_output_device", "TTS_OUTPUT_DEVICE"),
                ),
                discord=DiscordConfig(
                    bot_url=self._get_env_or_file_value(data, "discord_bot_url", "DISCORD_BOT_URL"),
                    member_id=self._get_env_or_file_value(data, "discord_member_id", "DISCORD_MEMBER_ID"),
                ),
                hotkey=HotkeyConfig(
                    trigger_open=data.get("trigger_open", "{"),
                    trigger_close=data.get("trigger_close", "}"),
                ),
                interface=InterfaceConfig(
                    show_notifications=data.get("show_notifications", True),
                    console_logs=data.get("console_logs", True),
                    local_tts_enabled=data.get("local_tts_enabled", False),
                ),
                network=NetworkConfig(
                    request_timeout=data.get("request_timeout", 10),
                    user_agent=data.get("user_agent", "TTS-Hotkey/2.0"),
                    max_text_length=data.get("max_text_length", 500),
                ),
            )
        except Exception as exc:
            print(f"[CONFIG] ⚠️ Erro ao carregar configuração: {exc}")
            return DesktopAppConfig.create_default()

    @staticmethod
    def _get_env_or_file_value(
        data: dict,
        file_key: str,
        env_key: str,
        default=None,
    ):
        """Prefer persisted values; fall back to env only for missing legacy keys."""
        if file_key in data:
            return data[file_key]

        return os.getenv(env_key, default)

    def save(self, config: DesktopAppConfig) -> bool:
        """Save configuration to file."""
        try:
            data = {
                "tts_engine": config.tts.engine,
                "tts_language": config.tts.language,
                "tts_voice_id": config.tts.voice_id,
                "tts_rate": config.tts.rate,
                "tts_output_device": config.tts.output_device,
                "discord_bot_url": config.discord.bot_url,
                "discord_member_id": config.discord.member_id,
                "trigger_open": config.hotkey.trigger_open,
                "trigger_close": config.hotkey.trigger_close,
                "show_notifications": config.interface.show_notifications,
                "console_logs": config.interface.console_logs,
                "local_tts_enabled": config.interface.local_tts_enabled,
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
