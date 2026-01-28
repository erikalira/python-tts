#!/usr/bin/env python3
"""
Standalone Module Init - Clean Architecture
Entry point for the standalone TTS Hotkey application.
"""

# Import with error handling for optional dependencies
try:
    from .config import *
    _config_available = True
except ImportError as e:
    print(f"[STANDALONE] ⚠️ Config import failed: {e}")
    _config_available = False

try:
    from .gui import *
    _gui_available = True
except ImportError as e:
    print(f"[STANDALONE] ⚠️ GUI import failed: {e}")
    _gui_available = False

try:
    from .services import *
    _services_available = True
except ImportError as e:
    print(f"[STANDALONE] ⚠️ Services import failed: {e}")
    _services_available = False

try:
    from .app import *
    _app_available = True
except ImportError as e:
    print(f"[STANDALONE] ⚠️ App import failed: {e}")
    _app_available = False

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