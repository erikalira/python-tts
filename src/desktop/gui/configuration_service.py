"""Service for choosing Desktop App configuration interfaces."""

from __future__ import annotations

from typing import Optional

from ..config.desktop_config import DesktopAppConfig


class ConfigurationService:
    """Service for managing configuration interfaces."""

    def __init__(self, prefer_gui: bool = True):
        self.prefer_gui = prefer_gui

    def get_configuration(self, current_config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Get configuration from user."""
        from . import simple_gui as compat
        from .config_dialogs import ConsoleConfig, GUIConfig

        if self.prefer_gui and compat.TKINTER_AVAILABLE:
            try:
                return GUIConfig().show_config(current_config)
            except Exception as exc:
                print(f"[CONFIG] âŒ Erro na GUI: {exc}")
                print("[CONFIG] ðŸ”„ Alternando para console...")
        return ConsoleConfig().show_config(current_config)
