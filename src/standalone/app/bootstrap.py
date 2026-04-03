"""Composition root for the Desktop App."""

from ..adapters.keyboard_backend import KeyboardHookBackend
from ..adapters.local_tts import Pyttsx3Adapter
from ..adapters.system_tray import create_system_tray_icon
from ..config.desktop_config import ConfigurationRepository
from ..gui.simple_gui import ConfigurationService
from ..services.discord_bot_client import HttpDiscordBotClient
from ..services.hotkey_services import HotkeyManager, HotkeyService, StandardKeyboardMonitor
from ..services.notification_services import ConsoleNotificationService, SystemTrayService
from ..services.tts_services import DesktopAppTTSService, KeyboardCleanupService, LocalPyTTSX3Engine
from .desktop_app import DesktopApp
from .tts_runtime import DesktopAppTTSProcessor


def create_desktop_application() -> DesktopApp:
    """Build the Desktop App with its concrete adapters."""

    def build_tts_processor(config):
        keyboard_backend = KeyboardHookBackend()
        bot_client = HttpDiscordBotClient(config)
        local_tts_adapter = Pyttsx3Adapter()
        tts_service = DesktopAppTTSService(
            config,
            bot_client=bot_client,
            local_engine_factory=lambda cfg: LocalPyTTSX3Engine(cfg, adapter=local_tts_adapter),
        )
        cleanup_service = KeyboardCleanupService(keyboard_backend=keyboard_backend)
        return DesktopAppTTSProcessor(
            tts_service=tts_service,
            cleanup_service=cleanup_service,
        )

    def build_hotkey_manager(config):
        keyboard_backend = KeyboardHookBackend()
        return HotkeyManager(
            config,
            service_factory=lambda cfg, handler: HotkeyService(
                cfg,
                handler,
                monitor_factory=lambda monitor_cfg, monitor_handler: StandardKeyboardMonitor(
                    monitor_cfg,
                    monitor_handler,
                    backend=keyboard_backend,
                ),
            ),
        )

    def build_notification_service(config):
        return SystemTrayService(
            config,
            tray_icon=create_system_tray_icon(config),
            notification_service=ConsoleNotificationService(),
        )

    return DesktopApp(
        config_repository=ConfigurationRepository(),
        config_service=ConfigurationService(prefer_gui=True),
        tts_processor_factory=build_tts_processor,
        hotkey_manager_factory=build_hotkey_manager,
        notification_service_factory=build_notification_service,
    )
