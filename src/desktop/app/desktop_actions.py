"""Action coordinators for the Windows Desktop App runtime."""

from __future__ import annotations

import logging
from typing import Optional
from collections.abc import Callable

from ..config.desktop_config import (
    DesktopAppConfig,
)
from src.application.dto import DesktopConfigurationSaveResultDTO
from ..gui.configuration_service import ConfigurationService
from .configuration_application import DesktopConfigurationApplicationService

logger = logging.getLogger(__name__)


class DesktopConfigurationCoordinator:
    """Coordinate configuration edits and their side effects for the Desktop App."""

    def __init__(
        self,
        config_service: ConfigurationService,
        configuration_application: DesktopConfigurationApplicationService,
    ):
        self._config_service = config_service
        self._configuration_application = configuration_application

    def handle_initial_configuration(
        self,
        current_config: DesktopAppConfig,
    ) -> tuple[bool, DesktopAppConfig]:
        """Run first-time configuration when required."""
        if self._configuration_application.is_configured(current_config):
            return True, current_config

        logger.info("[DESKTOP_APP] First run detected, opening initial setup")
        updated_config = self._config_service.get_configuration(current_config)
        if not updated_config:
            return False, current_config

        self._configuration_application.apply(updated_config)
        return True, updated_config

    def save_from_ui(self, updated_config: DesktopAppConfig) -> DesktopConfigurationSaveResultDTO:
        """Validate, persist, and apply configuration changes from the main window."""
        is_valid, errors = self._configuration_application.validate(updated_config)
        if not is_valid:
            message = "; ".join(errors)
            logger.error("[DESKTOP_APP] Invalid configuration received from the interface: %s", message)
            return DesktopConfigurationSaveResultDTO(success=False, message=message)

        save_success = self._configuration_application.apply(updated_config)
        logger.info("[DESKTOP_APP] Configuration saved from the main panel")
        return DesktopConfigurationSaveResultDTO(
            success=True,
            message=(
                "Configuration applied successfully"
                if save_success
                else "Configuration applied, but the file could not be persisted"
            ),
        )

    def reconfigure(
        self,
        current_config: DesktopAppConfig,
        hotkeys_were_active: bool,
        resume_hotkeys: Callable[[], None],
        notify_error: Optional[Callable[[str, str], None]] = None,
        notify_success: Optional[Callable[[str, str], None]] = None,
        are_hotkeys_active: Optional[Callable[[], bool]] = None,
    ) -> tuple[Optional[DesktopAppConfig], bool]:
        """Open configuration UI and apply changes from the tray flow."""
        updated_config = None
        try:
            updated_config = self._config_service.get_configuration(current_config)
        finally:
            if hotkeys_were_active and not updated_config:
                resume_hotkeys()

        if not updated_config:
            logger.info("[DESKTOP_APP] Configuration canceled")
            return None, False

        is_valid, errors = self._configuration_application.validate(updated_config)
        if not is_valid:
            logger.error("[DESKTOP_APP] Invalid configuration: %s", "; ".join(errors))
            if notify_error:
                notify_error("Desktop App", "Invalid configuration")
            if hotkeys_were_active:
                resume_hotkeys()
            return None, False

        self._configuration_application.apply(updated_config)
        if hotkeys_were_active and are_hotkeys_active and not are_hotkeys_active():
            resume_hotkeys()

        logger.info("[DESKTOP_APP] Configuration updated successfully")
        if notify_success:
            notify_success("Desktop App", "Configuration updated")
        return updated_config, True
