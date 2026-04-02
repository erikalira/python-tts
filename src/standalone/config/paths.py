#!/usr/bin/env python3
"""Filesystem paths for standalone configuration."""

import os
from pathlib import Path


def get_config_directory() -> Path:
    """Get configuration directory following OS best practices."""
    if os.name == "nt":
        config_dir = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / "TTS-Hotkey"
    else:
        config_dir = Path.home() / ".config" / "tts-hotkey"

    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir
