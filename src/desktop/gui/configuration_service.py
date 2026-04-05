"""Service for choosing Desktop App configuration interfaces."""

from __future__ import annotations

import logging
from typing import Callable, Optional

from ..config.desktop_config import DesktopAppConfig
from . import tk_support
from .config_dialogs import ConfigInterface, ConsoleConfig, GUIConfig

logger = logging.getLogger(__name__)


class ConfigurationService:
    """Service for managing configuration interfaces."""

    def __init__(
        self,
        prefer_gui: bool = True,
        gui_factory: Callable[[], ConfigInterface] = GUIConfig,
        console_factory: Callable[[], ConfigInterface] = ConsoleConfig,
    ):
        self.prefer_gui = prefer_gui
        self._gui_factory = gui_factory
        self._console_factory = console_factory

    def get_configuration(self, current_config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Get configuration from user."""
        if self.prefer_gui and tk_support.TKINTER_AVAILABLE:
            try:
                return self._gui_factory().show_config(current_config)
            except Exception as exc:
                logger.error("[CONFIG] GUI error: %s", exc)
                logger.info("[CONFIG] Falling back to console...")
        return self._console_factory().show_config(current_config)
