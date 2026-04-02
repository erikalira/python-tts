#!/usr/bin/env python3
"""Configuration models for the standalone application."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file once for standalone defaults.
load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=True)


@dataclass
class TTSConfig:
    """TTS Engine configuration."""

    engine: str = os.getenv("TTS_ENGINE", "gtts")
    language: str = os.getenv("TTS_LANGUAGE", "pt")
    voice_id: str = os.getenv("TTS_VOICE_ID", "roa/pt-br")
    rate: int = int(os.getenv("TTS_RATE", "180"))
    output_device: Optional[str] = os.getenv("TTS_OUTPUT_DEVICE")


@dataclass
class DiscordConfig:
    """Discord bot configuration."""

    bot_url: str = os.getenv("DISCORD_BOT_URL", "localhost:10000")
    guild_id: Optional[str] = os.getenv("DISCORD_GUILD_ID")
    channel_id: Optional[str] = os.getenv("DISCORD_CHANNEL_ID")
    member_id: Optional[str] = os.getenv("DISCORD_MEMBER_ID")


@dataclass
class HotkeyConfig:
    """Hotkey configuration."""

    trigger_open: str = "{"
    trigger_close: str = "}"

    @property
    def keys(self) -> str:
        """Get formatted hotkey display string."""
        return f"{self.trigger_open}text{self.trigger_close}"


@dataclass
class InterfaceConfig:
    """Interface configuration."""

    show_notifications: bool = True
    console_logs: bool = True


@dataclass
class NetworkConfig:
    """Network configuration."""

    request_timeout: int = 10
    user_agent: str = "TTS-Hotkey/2.0"
    max_text_length: int = 500


@dataclass
class StandaloneConfig:
    """Main configuration container for standalone application."""

    tts: TTSConfig
    discord: DiscordConfig
    hotkey: HotkeyConfig
    interface: InterfaceConfig
    network: NetworkConfig

    @classmethod
    def create_default(cls) -> "StandaloneConfig":
        """Create configuration with default values."""
        return cls(
            tts=TTSConfig(),
            discord=DiscordConfig(),
            hotkey=HotkeyConfig(),
            interface=InterfaceConfig(),
            network=NetworkConfig(),
        )
