#!/usr/bin/env python3
"""
Notification and System Tray Services - Clean Architecture (Fixed)
Provides system tray icon and notification services.
"""

import logging
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Optional, Protocol

from src.application.dto import SystemTrayStatusDTO

from ..adapters.system_tray import (
    NullSystemTrayIcon as _NullSystemTrayIcon,
)
from ..adapters.system_tray import (
    create_system_tray_icon,
    is_system_tray_available,
)
from ..config.desktop_config import DesktopAppConfig

NullSystemTrayIcon = _NullSystemTrayIcon
logger = logging.getLogger(__name__)


class NotificationService(ABC):
    """Abstract interface for notification services."""

    @abstractmethod
    def show_info(self, title: str, message: str) -> None:
        """Show an informational notification."""

    @abstractmethod
    def show_success(self, title: str, message: str) -> None:
        """Show a success notification."""

    @abstractmethod
    def show_error(self, title: str, message: str) -> None:
        """Show an error notification."""

    @abstractmethod
    def is_available(self) -> bool:
        """Check if notification service is available."""


class ConsoleNotificationService(NotificationService):
    """Console-based notification service."""

    def show_info(self, title: str, message: str) -> None:
        logger.info("[INFO] %s: %s", title, message)

    def show_success(self, title: str, message: str) -> None:
        logger.info("[OK] %s: %s", title, message)

    def show_error(self, title: str, message: str) -> None:
        logger.error("[ERROR] %s: %s", title, message)

    def is_available(self) -> bool:
        return True


class SystemTrayIcon(Protocol):
    """Protocol for system tray functionality."""

    def show(self) -> None:
        """Show the system tray icon."""
        ...

    def hide(self) -> None:
        """Hide the system tray icon."""
        ...

    def set_tooltip(self, tooltip: str) -> None:
        """Set the tooltip text."""
        ...

    def is_available(self) -> bool:
        """Check if system tray is available."""
        ...

    def is_running(self) -> bool:
        """Check if the tray loop is running."""
        ...

    def set_handlers(
        self,
        status_click: Optional[Callable[[], None]] = None,
        configure: Optional[Callable[[], None]] = None,
        quit_handler: Optional[Callable[[], None]] = None,
    ) -> None:
        """Set callback handlers for tray actions."""
        ...


class SystemTrayService:
    """Service for managing system tray functionality."""

    _TRAY_START_TIMEOUT_SECONDS = 1.0
    _TRAY_START_POLL_INTERVAL_SECONDS = 0.05

    def __init__(
        self,
        config: DesktopAppConfig,
        tray_icon: Optional[SystemTrayIcon] = None,
        notification_service: Optional[NotificationService] = None,
    ):
        self._config = config
        self._tray_icon = tray_icon or self._create_tray_icon()
        self._notification_service = notification_service or ConsoleNotificationService()
        self._tray_thread: Optional[threading.Thread] = None

    def _create_tray_icon(self) -> SystemTrayIcon:
        """Create appropriate system tray icon based on availability."""
        return create_system_tray_icon(self._config)

    def initialize(
        self,
        status_click: Optional[Callable[[], None]] = None,
        configure: Optional[Callable[[], None]] = None,
        quit_handler: Optional[Callable[[], None]] = None,
    ) -> None:
        """Initialize system tray with handlers."""
        self._tray_icon.set_handlers(status_click, configure, quit_handler)

    def start(self) -> bool:
        """Start system tray service only after startup is confirmed."""
        if not self._tray_icon.is_available():
            logger.info("[TRAY] System tray is not available, running in console mode")
            return False

        if self.is_running():
            return True

        self._tray_thread = threading.Thread(
            target=self._tray_icon.show,
            name="desktop-app-system-tray",
            daemon=True,
        )
        self._tray_thread.start()

        deadline = time.monotonic() + self._TRAY_START_TIMEOUT_SECONDS
        while time.monotonic() < deadline:
            if self.is_running():
                return True
            if self._tray_thread is None or not self._tray_thread.is_alive():
                break
            time.sleep(self._TRAY_START_POLL_INTERVAL_SECONDS)

        logger.warning("[TRAY] System tray did not confirm startup, continuing without tray")
        self._tray_thread = None
        return False

    def run_tray(self) -> None:
        """Run system tray (blocking call)."""
        if self._tray_icon.is_available():
            self._tray_icon.show()
        else:
            logger.info("[TRAY] System tray is not available, continuing in console mode...")
            try:
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                pass

    def stop(self) -> None:
        """Stop system tray service."""
        self._tray_icon.hide()
        if self._tray_thread and self._tray_thread.is_alive():
            self._tray_thread.join(timeout=1.0)
        self._tray_thread = None

    def notify_info(self, title: str, message: str) -> None:
        if self._config.interface.show_notifications:
            self._notification_service.show_info(title, message)

    def notify_success(self, title: str, message: str) -> None:
        if self._config.interface.show_notifications:
            self._notification_service.show_success(title, message)

    def notify_error(self, title: str, message: str) -> None:
        if self._config.interface.show_notifications:
            self._notification_service.show_error(title, message)

    def is_available(self) -> bool:
        """Check if system tray support exists in the environment."""
        return self._tray_icon.is_available()

    def is_running(self) -> bool:
        """Check if the tray loop is actually running."""
        if hasattr(self._tray_icon, "is_running"):
            return bool(self._tray_icon.is_running())
        return bool(self._tray_thread and self._tray_thread.is_alive())

    def get_status(self) -> SystemTrayStatusDTO:
        """Get system tray service status."""
        return SystemTrayStatusDTO(
            tray_available=self._tray_icon.is_available(),
            tray_running=self.is_running(),
            pystray_installed=is_system_tray_available(),
            notifications_enabled=self._config.interface.show_notifications,
        )
