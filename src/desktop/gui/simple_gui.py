#!/usr/bin/env python3
"""Compatibility facade for Desktop App GUI modules."""

import logging

from ..config.desktop_config import ConfigurationValidator

try:
    import tkinter as tk
    from tkinter import messagebox, ttk

    TKINTER_AVAILABLE = True
except ImportError:
    tk = None
    ttk = None
    messagebox = None
    TKINTER_AVAILABLE = False

logger = logging.getLogger(__name__)

from .config_dialogs import ConfigInterface, ConsoleConfig, GUIConfig, InitialSetupGUI
from .configuration_service import ConfigurationService
from .main_window import DesktopAppMainWindow
from .ui_logging import UILogHandler

__all__ = [
    "ConfigInterface",
    "ConsoleConfig",
    "ConfigurationValidator",
    "ConfigurationService",
    "DesktopAppMainWindow",
    "GUIConfig",
    "InitialSetupGUI",
    "TKINTER_AVAILABLE",
    "UILogHandler",
    "logger",
    "messagebox",
    "tk",
    "ttk",
]
