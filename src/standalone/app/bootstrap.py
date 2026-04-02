"""Composition root for the standalone application."""

from ..config.standalone_config import ConfigurationRepository
from ..gui.simple_gui import ConfigurationService
from ..services.hotkey_services import HotkeyManager
from ..services.notification_services import SystemTrayService
from ..services.tts_services import TTSProcessor
from .standalone_app import StandaloneApplication


def create_standalone_application() -> StandaloneApplication:
    """Build the standalone application with its concrete adapters."""
    return StandaloneApplication(
        config_repository=ConfigurationRepository(),
        config_service=ConfigurationService(prefer_gui=True),
        tts_processor_factory=TTSProcessor,
        hotkey_manager_factory=HotkeyManager,
        notification_service_factory=SystemTrayService,
    )
