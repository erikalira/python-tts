"""Service for choosing Desktop App configuration interfaces."""

from __future__ import annotations

from typing import Optional

from ..config.desktop_config import DesktopAppConfig
from . import tk_support
from .config_dialogs import ConsoleConfig, GUIConfig


class ConfigurationService:
    """Service for managing configuration interfaces."""

    def __init__(self, prefer_gui: bool = True):
        self.prefer_gui = prefer_gui

    def get_configuration(self, current_config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Get configuration from user."""
        if self.prefer_gui and tk_support.TKINTER_AVAILABLE:
            try:
                return GUIConfig().show_config(current_config)
            except Exception as exc:
                print(f"[CONFIG] GUI error: {exc}")
                print("[CONFIG] Falling back to console...")
        return ConsoleConfig().show_config(current_config)
