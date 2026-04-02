#!/usr/bin/env python3
"""Compatibility facade for standalone configuration modules."""

import os

from .environment import EnvironmentUpdater
from .models import (
    DiscordConfig,
    HotkeyConfig,
    InterfaceConfig,
    NetworkConfig,
    StandaloneConfig,
    TTSConfig,
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
    "StandaloneConfig",
    "ConfigurationRepository",
    "EnvironmentUpdater",
    "ConfigurationValidator",
    "get_config_directory",
    "os",
]
