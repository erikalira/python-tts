#!/usr/bin/env python3
"""
Standalone Module Init - Clean Architecture
Entry point for the standalone TTS Hotkey application.
"""

from .config import *
from .gui import *
from .services import *
from .app import *

__all__ = [
    # Config
    'TTSConfig',
    'DiscordConfig', 
    'HotkeyConfig',
    'InterfaceConfig',
    'NetworkConfig',
    'StandaloneConfig',
    'ConfigurationRepository',
    'EnvironmentUpdater',
    'ConfigurationValidator',
    
    # GUI
    'ConfigurationInterface',
    'ConsoleConfigurationInterface',
    'GUIConfigurationInterface',
    'ConfigurationUIFactory',
    'ConfigurationDisplayService',
    
    # Services
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
    'HotkeyManager',
    'NotificationService',
    'ConsoleNotificationService',
    'SystemTrayIcon',
    'PySystemTrayIcon',
    'NullSystemTrayIcon',
    'SystemTrayService',
    
    # App
    'StandaloneHotkeyHandler',
    'StandaloneApplication',
    'create_standalone_application',
    'main'
]