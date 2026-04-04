#!/usr/bin/env python3
"""Filesystem paths for Desktop App configuration."""

import os
from pathlib import Path


def get_config_directory() -> Path:
    """Get configuration directory following OS best practices."""
    local_appdata = os.getenv("LOCALAPPDATA")
    legacy_windows_name = "TTS-Hotkey"
    current_windows_name = "DesktopApp"

    if local_appdata:
        legacy_dir = Path(local_appdata) / legacy_windows_name
        config_dir = legacy_dir if legacy_dir.exists() else Path(local_appdata) / current_windows_name
    elif os.name == "nt":
        local_root = Path.home() / "AppData" / "Local"
        legacy_dir = local_root / legacy_windows_name
        config_dir = legacy_dir if legacy_dir.exists() else local_root / current_windows_name
    else:
        config_dir = Path.home() / ".config" / "desktop-app"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
