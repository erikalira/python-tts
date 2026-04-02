#!/usr/bin/env python3
"""
Notification and System Tray Services - Clean Architecture (Fixed)
Provides system tray icon and notification services.
"""

from abc import ABC, abstractmethod
import threading
from typing import Callable, Optional

from ..config.standalone_config import StandaloneConfig
from ..adapters.system_tray import (
    NullSystemTrayIcon as _NullSystemTrayIcon,
    create_system_tray_icon,
    is_system_tray_available,
)

NullSystemTrayIcon = _NullSystemTrayIcon


class NotificationService(ABC):
    """Abstract interface for notification services."""
    
    @abstractmethod
    def show_info(self, title: str, message: str) -> None:
        """Show an informational notification."""
        pass
    
    @abstractmethod
    def show_success(self, title: str, message: str) -> None:
        """Show a success notification."""
        pass
    
    @abstractmethod
    def show_error(self, title: str, message: str) -> None:
        """Show an error notification."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if notification service is available."""
        pass


class ConsoleNotificationService(NotificationService):
    """Console-based notification service."""
    
    def show_info(self, title: str, message: str) -> None:
        """Show info message in console."""
        print(f"ℹ️ {title}: {message}")
    
    def show_success(self, title: str, message: str) -> None:
        """Show success message in console."""
        print(f"✅ {title}: {message}")
    
    def show_error(self, title: str, message: str) -> None:
        """Show error message in console."""
        print(f"❌ {title}: {message}")
    
    def is_available(self) -> bool:
        """Console is always available."""
        return True


class SystemTrayIcon(ABC):
    """Abstract interface for system tray functionality."""
    
    @abstractmethod
    def show(self) -> None:
        """Show the system tray icon."""
        pass
    
    @abstractmethod
    def hide(self) -> None:
        """Hide the system tray icon."""
        pass
    
    @abstractmethod
    def set_tooltip(self, tooltip: str) -> None:
        """Set the tooltip text."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if system tray is available."""
        pass


class SystemTrayService:
    """Service for managing system tray functionality."""
    
    def __init__(
        self,
        config: StandaloneConfig,
        tray_icon: Optional[object] = None,
        notification_service: Optional[NotificationService] = None
    ):
        self._config = config
        self._tray_icon = tray_icon or self._create_tray_icon()
        self._notification_service = notification_service or ConsoleNotificationService()
        self._tray_thread: Optional[threading.Thread] = None
    
    def _create_tray_icon(self) -> SystemTrayIcon:
        """Create appropriate system tray icon based on availability."""
        return create_system_tray_icon(self._config)
    
    def initialize(self, 
                  status_click: Optional[Callable] = None,
                  configure: Optional[Callable] = None,
                  quit_handler: Optional[Callable] = None) -> None:
        """Initialize system tray with handlers."""
        if hasattr(self._tray_icon, 'set_handlers'):
            self._tray_icon.set_handlers(status_click, configure, quit_handler)
    
    def start(self) -> bool:
        """Start system tray service."""
        if not self._tray_icon.is_available():
            print("[TRAY] ⚠️ System tray não disponível, executando em modo console")
            return False

        if self._tray_thread and self._tray_thread.is_alive():
            return True

        self._tray_thread = threading.Thread(
            target=self._tray_icon.show,
            name="standalone-system-tray",
            daemon=True,
        )
        self._tray_thread.start()
        return True
    
    def run_tray(self) -> None:
        """Run system tray (blocking call)."""
        if self._tray_icon.is_available():
            self._tray_icon.show()
        else:
            print("[TRAY] ⚠️ System tray não disponível, continuando em modo console...")
            # Keep running in console mode
            try:
                import time
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
        """Send informational notification."""
        if self._config.interface.show_notifications:
            self._notification_service.show_info(title, message)
    
    def notify_success(self, title: str, message: str) -> None:
        """Send success notification."""
        if self._config.interface.show_notifications:
            self._notification_service.show_success(title, message)
    
    def notify_error(self, title: str, message: str) -> None:
        """Send error notification."""
        if self._config.interface.show_notifications:
            self._notification_service.show_error(title, message)
    
    def is_available(self) -> bool:
        """Check if system tray is available."""
        return self._tray_icon.is_available()
    
    def get_status(self) -> dict:
        """Get system tray service status."""
        return {
            'tray_available': self._tray_icon.is_available(),
            'pystray_installed': is_system_tray_available(),
            'notifications_enabled': self._config.interface.show_notifications
        }
