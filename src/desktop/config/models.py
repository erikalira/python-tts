#!/usr/bin/env python3
"""Configuration models for the Desktop App."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from src.core.entities import TTSConfig

# Load environment variables from .env file once for Desktop App defaults.
load_dotenv(Path(__file__).resolve().parents[3] / ".env", override=True)


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
    local_tts_enabled: bool = False


@dataclass
class NetworkConfig:
    """Network configuration."""

    request_timeout: int = 10
    user_agent: str = "TTS-Hotkey/2.0"
    max_text_length: int = 500


@dataclass
class DesktopAppConfig:
    """Main configuration container for the Desktop App."""

    tts: TTSConfig
    discord: DiscordConfig
    hotkey: HotkeyConfig
    interface: InterfaceConfig
    network: NetworkConfig

    @classmethod
    def create_default(cls) -> "DesktopAppConfig":
        """Create configuration with default values."""
        return cls(
            tts=TTSConfig(
                engine=os.getenv("TTS_ENGINE", "gtts"),
                language=os.getenv("TTS_LANGUAGE", "pt"),
                voice_id=os.getenv("TTS_VOICE_ID", "roa/pt-br"),
                rate=int(os.getenv("TTS_RATE", "180")),
                output_device=os.getenv("TTS_OUTPUT_DEVICE"),
            ),
            discord=DiscordConfig(),
            hotkey=HotkeyConfig(),
            interface=InterfaceConfig(),
            network=NetworkConfig(),
        )
