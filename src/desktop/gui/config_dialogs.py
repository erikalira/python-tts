"""Compatibility facade for Desktop App configuration dialog flows."""

from .config_dialog_contracts import ConfigInterface
from .initial_setup_dialog import InitialSetupGUI
from .settings_console_dialog import ConsoleConfig
from .settings_gui_dialog import GUIConfig

__all__ = [
    "ConfigInterface",
    "ConsoleConfig",
    "GUIConfig",
    "InitialSetupGUI",
]
