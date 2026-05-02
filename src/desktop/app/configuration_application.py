"""Application services for Desktop App configuration flows."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Optional, Protocol

from ..config.desktop_config import (
    ConfigurationValidator,
    DesktopAppConfig,
    EnvironmentUpdater,
)

logger = logging.getLogger(__name__)


class DesktopConfigRepository(Protocol):
    """Port for Desktop App configuration persistence."""

    def save(self, config: DesktopAppConfig) -> bool:
        """Persist the provided Desktop App configuration."""
        ...


class DesktopConfigEnvironment(Protocol):
    """Port for synchronizing Desktop App configuration into the environment."""

    def update_from_config(self, config: DesktopAppConfig) -> None:
        """Synchronize runtime environment variables from configuration."""


class DesktopConfigurationApplicationService:
    """Validate, persist, and apply Desktop App configuration side effects."""

    def __init__(
        self,
        config_repository: DesktopConfigRepository,
        update_services: Callable[[], None],
        environment_updater: Optional[DesktopConfigEnvironment] = None,
    ):
        self._config_repository = config_repository
        self._update_services = update_services
        self._environment_updater = environment_updater or EnvironmentUpdater

    def is_configured(self, config: DesktopAppConfig) -> bool:
        """Return whether the Desktop App has minimum required configuration."""
        return ConfigurationValidator.is_configured(config)

    def validate(self, config: DesktopAppConfig) -> tuple[bool, list[str]]:
        """Validate the provided Desktop App configuration."""
        return ConfigurationValidator.validate(config)

    def apply(self, config: DesktopAppConfig) -> bool:
        """Persist configuration and apply its runtime side effects."""
        save_success = self._config_repository.save(config)
        if not save_success:
            logger.warning(
                "[DESKTOP_APP] Failed to save configuration, continuing with in-memory configuration"
            )

        self._environment_updater.update_from_config(config)
        self._update_services()
        return save_success
