#!/usr/bin/env python3
"""Public exports for the Desktop App runtime."""

from .desktop_app import (
    DesktopApp,
    create_desktop_application,
    main,
)
from .tts_runtime import DesktopAppHotkeyHandler

__all__ = [
    "DesktopApp",
    "DesktopAppHotkeyHandler",
    "create_desktop_application",
    "main",
]
