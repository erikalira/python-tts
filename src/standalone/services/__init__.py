#!/usr/bin/env python3
"""
Standalone Services Module Init
"""

from .tts_services import (
    TTSEngine,
    LocalPyTTSX3Engine,
    DiscordTTSService,
    FallbackTTSEngine,
    TTSService,
    KeyboardCleanupService,
    TTSProcessor
)

from .hotkey_services import (
    HotkeyEvent,
    HotkeyHandler,
    KeyboardMonitor,
    StandardKeyboardMonitor,
    HotkeyService,
    HotkeyManager
)

try:
    from .notification_services import (
        NotificationService,
        ConsoleNotificationService,
        SystemTrayIcon,
        PySystemTrayIcon,
        NullSystemTrayIcon,
        SystemTrayService
    )
    _notification_available = True
except ImportError as e:
    print(f"[SERVICES] ⚠️ Notification services not available: {e}")
    _notification_available = False

# Base exports (always available)
__all__ = [
    'TTSEngine',
    'LocalPyTTSX3Engine',
    'DiscordTTSService',
    'FallbackTTSEngine',
    'TTSService',
    'KeyboardCleanupService',
    'TTSProcessor',
    'HotkeyEvent',
    'HotkeyHandler',
    'KeyboardMonitor',
    'StandardKeyboardMonitor',
    'HotkeyService',
    'HotkeyManager'
]

# Add notification services if available
if _notification_available:
    __all__.extend([
        'NotificationService',
        'ConsoleNotificationService',
        'SystemTrayIcon',
        'PySystemTrayIcon',
        'NullSystemTrayIcon',
        'SystemTrayService'
    ])