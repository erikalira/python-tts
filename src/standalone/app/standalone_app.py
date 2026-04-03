"""Compatibility exports for the Desktop App runtime module."""

from .desktop_app import (
    DesktopApp,
    StandaloneApplication,
    create_desktop_application,
    create_standalone_application,
    main,
)
from .tts_runtime import (
    DesktopAppHotkeyHandler,
    DesktopAppTTSResultPresenter,
    StandaloneHotkeyHandler,
    StandaloneTTSResultPresenter,
)

__all__ = [
    "DesktopApp",
    "DesktopAppHotkeyHandler",
    "DesktopAppTTSResultPresenter",
    "StandaloneApplication",
    "StandaloneHotkeyHandler",
    "StandaloneTTSResultPresenter",
    "create_desktop_application",
    "create_standalone_application",
    "main",
]
