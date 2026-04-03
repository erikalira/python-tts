#!/usr/bin/env python3
"""Public Desktop App configuration facade."""

import os

from .environment import EnvironmentUpdater
from .models import (
    DesktopAppConfig,
    DiscordConfig,
    HotkeyConfig,
    InterfaceConfig,
    NetworkConfig,
    TTSConfig,
    get_default_discord_bot_url,
)
from .paths import get_config_directory
from .repository import ConfigurationRepository
from .validation import ConfigurationValidator

__all__ = [
    "TTSConfig",
    "DiscordConfig",
    "HotkeyConfig",
    "InterfaceConfig",
    "NetworkConfig",
    "DesktopAppConfig",
    "ConfigurationRepository",
    "EnvironmentUpdater",
    "ConfigurationValidator",
    "get_default_discord_bot_url",
    "get_config_directory",
    "os",
]
