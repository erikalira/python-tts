#!/usr/bin/env python3
"""
Notification and System Tray Services - Clean Architecture (Fixed)
Provides system tray icon and notification services.
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional

try:
    from pystray import Icon, Menu, MenuItem
    from PIL import Image, ImageDraw
    _pystray_available = True
except Exception as e:
    print(f"[NOTIFICATION] ⚠️ pystray not available: {e}")
    _pystray_available = False

from ..config.standalone_config import StandaloneConfig


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


class NullSystemTrayIcon(SystemTrayIcon):
    """Null object pattern for when system tray is not available."""
    
    def show(self) -> None:
        """No-op for show."""
        pass
    
    def hide(self) -> None:
        """No-op for hide."""
        pass
    
    def set_tooltip(self, tooltip: str) -> None:
        """No-op for set tooltip."""
        pass
    
    def is_available(self) -> bool:
        """Always returns False."""
        return False


if _pystray_available:
    class PySystemTrayIcon(SystemTrayIcon):
        """System tray icon using pystray library."""
        
        def __init__(self, config: StandaloneConfig):
            self._config = config
            self._icon: Optional[Icon] = None
            self._running = False
            
            # Callback handlers
            self._on_status_click: Optional[Callable] = None
            self._on_configure: Optional[Callable] = None
            self._on_quit: Optional[Callable] = None
        
        def set_handlers(self, 
                        status_click: Optional[Callable] = None,
                        configure: Optional[Callable] = None,
                        quit_handler: Optional[Callable] = None) -> None:
            """Set callback handlers for menu actions."""
            self._on_status_click = status_click
            self._on_configure = configure
            self._on_quit = quit_handler
        
        def show(self) -> None:
            """Show system tray icon (blocking call)."""
            if self._running:
                return
            
            try:
                self._icon = self._create_icon()
                self._running = True
                print("[TRAY] ✅ System tray iniciado")
                self._icon.run()  # This is a blocking call
            except Exception as e:
                print(f"[TRAY] ❌ Erro ao iniciar system tray: {e}")
                self._running = False
        
        def hide(self) -> None:
            """Hide system tray icon."""
            if self._icon and self._running:
                try:
                    self._icon.stop()
                    self._running = False
                    print("[TRAY] 🛑 System tray parado")
                except Exception as e:
                    print(f"[TRAY] ⚠️ Erro ao parar system tray: {e}")
        
        def set_tooltip(self, tooltip: str) -> None:
            """Set tooltip text."""
            if self._icon:
                self._icon.title = tooltip
        
        def is_available(self) -> bool:
            """Check if pystray is available."""
            return True
        
        def _create_icon(self) -> Icon:
            """Create the system tray icon."""
            menu = Menu(
                MenuItem('TTS Hotkey', self._handle_status_click, default=True),
                MenuItem(f'Digite {self._config.hotkey.trigger_open}texto{self._config.hotkey.trigger_close} para falar', 
                        lambda: None, enabled=False),
                Menu.SEPARATOR,
                MenuItem('⚙️ Configurações', self._handle_configure),
                MenuItem('Sair', self._handle_quit)
            )
            
            icon_image = self._create_icon_image()
            return Icon("TTS Hotkey", icon_image, "TTS Hotkey", menu)
        
        def _create_icon_image(self) -> Image.Image:
            """Create the icon image."""
            try:
                # Try to load custom icon first
                icon_path = Path(__file__).resolve().parents[3] / "assets" / "icon.png"
                if icon_path.exists():
                    return Image.open(icon_path)
            except Exception:
                pass
            
            # Fallback: create simple icon
            img = Image.new('RGB', (64, 64), color='#2C2F33')
            draw = ImageDraw.Draw(img)
            
            # Draw microphone shape
            draw.rectangle([22, 15, 42, 35], fill='#7289DA')  # Mic body
            draw.ellipse([22, 30, 42, 45], fill='#7289DA')    # Mic mesh
            
            return img
        
        def _handle_status_click(self, icon, item) -> None:
            """Handle status click."""
            if self._on_status_click:
                self._on_status_click()
            else:
                self._default_status_click()
        
        def _handle_configure(self, icon, item) -> None:
            """Handle configure action."""
            if self._on_configure:
                self._on_configure()
            else:
                print("🔧 Configurações não disponíveis")
        
        def _handle_quit(self, icon, item) -> None:
            """Handle quit action."""
            if self._on_quit:
                self._on_quit()
            else:
                self._default_quit()
        
        def _default_status_click(self) -> None:
            """Default status click handler."""
            if self._config.discord.bot_url and self._config.discord.member_id:
                print(f"✅ Conectado ao Discord: {self._config.discord.bot_url}")
                print(f"👤 User ID: {self._config.discord.member_id}")
            else:
                print("⚠️ Discord não configurado completamente")
        
        def _default_quit(self) -> None:
            """Default quit handler."""
            print("🛑 Encerrando TTS Hotkey...")
            self.hide()
            os._exit(0)

else:
    # Create dummy class when pystray is not available
    PySystemTrayIcon = NullSystemTrayIcon


class SystemTrayService:
    """Service for managing system tray functionality."""
    
    def __init__(self, config: StandaloneConfig):
        self._config = config
        self._tray_icon = self._create_tray_icon()
        self._notification_service = ConsoleNotificationService()
    
    def _create_tray_icon(self) -> SystemTrayIcon:
        """Create appropriate system tray icon based on availability."""
        if _pystray_available:
            return PySystemTrayIcon(self._config)
        else:
            return NullSystemTrayIcon()
    
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
        
        self._tray_icon.show()
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
            'pystray_installed': _pystray_available,
            'notifications_enabled': self._config.interface.show_notifications
        }
