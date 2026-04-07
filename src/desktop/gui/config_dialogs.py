"""Public entrypoint for Desktop App configuration dialog flows.

This module intentionally keeps the main dialog imports behind a small,
stable surface so Desktop App callers do not depend on the internal file
layout of the GUI package.
"""

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
