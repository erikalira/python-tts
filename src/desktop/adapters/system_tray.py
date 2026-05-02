#!/usr/bin/env python3
"""System tray adapters for Desktop App services."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:
    from PIL import Image, ImageDraw
    from pystray import Icon, Menu, MenuItem

    _pystray_available = True
except Exception as exc:
    logger.warning("pystray not available: %s", exc)
    Icon = Menu = MenuItem = Image = ImageDraw = None
    _pystray_available = False

from ..config.desktop_config import DesktopAppConfig


class SystemTrayIconAdapter:
    """Abstractable base for system tray adapters."""

    def show(self) -> None:
        raise NotImplementedError

    def hide(self) -> None:
        raise NotImplementedError

    def set_tooltip(self, tooltip: str) -> None:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError

    def is_running(self) -> bool:
        raise NotImplementedError

    def set_handlers(
        self,
        status_click: Callable[[], None] | None = None,
        configure: Callable[[], None] | None = None,
        quit_handler: Callable[[], None] | None = None,
    ) -> None:
        """Set callback handlers for tray actions."""
        raise NotImplementedError


class NullSystemTrayIcon(SystemTrayIconAdapter):
    """Null object used when no tray implementation is available."""

    def show(self) -> None:
        pass

    def hide(self) -> None:
        pass

    def set_tooltip(self, tooltip: str) -> None:
        pass

    def is_available(self) -> bool:
        return False

    def is_running(self) -> bool:
        return False

    def set_handlers(
        self,
        status_click: Callable[[], None] | None = None,
        configure: Callable[[], None] | None = None,
        quit_handler: Callable[[], None] | None = None,
    ) -> None:
        pass


class PySystemTrayIcon(SystemTrayIconAdapter):
    """pystray-backed system tray adapter."""

    def __init__(self, config: DesktopAppConfig):
        self._config = config
        self._icon: Any | None = None
        self._running = False
        self._on_status_click: Callable[[], None] | None = None
        self._on_configure: Callable[[], None] | None = None
        self._on_quit: Callable[[], None] | None = None

    def set_handlers(
        self,
        status_click: Callable[[], None] | None = None,
        configure: Callable[[], None] | None = None,
        quit_handler: Callable[[], None] | None = None,
    ) -> None:
        """Set callback handlers for tray actions."""
        self._on_status_click = status_click
        self._on_configure = configure
        self._on_quit = quit_handler

    def show(self) -> None:
        """Show system tray icon."""
        if self._running:
            return

        try:
            icon = self._create_icon()
            self._icon = icon
            self._running = True
            logger.info("[TRAY] System tray started")
            icon.run()
        except Exception as exc:
            logger.error("[TRAY] Failed to start system tray: %s", exc)
            self._running = False

    def hide(self) -> None:
        """Hide system tray icon."""
        if self._icon and self._running:
            try:
                self._icon.stop()
                self._running = False
                logger.info("[TRAY] System tray stopped")
            except Exception as exc:
                logger.warning("[TRAY] Failed to stop system tray: %s", exc)

    def set_tooltip(self, tooltip: str) -> None:
        """Set tooltip text."""
        if self._icon:
            self._icon.title = tooltip

    def is_available(self) -> bool:
        """pystray adapter is available when constructed."""
        return True

    def is_running(self) -> bool:
        """Return whether the tray event loop is running."""
        return self._running

    def _create_icon(self) -> Any:
        if Icon is None or Menu is None or MenuItem is None:
            raise RuntimeError("pystray unavailable")

        menu = Menu(
            MenuItem("Open Desktop App", self._handle_status_click, default=True),
            MenuItem(
                f"Type {self._config.hotkey.trigger_open}text{self._config.hotkey.trigger_close} to speak",
                lambda: None,
                enabled=False,
            ),
            Menu.SEPARATOR,
            MenuItem("Settings", self._handle_configure),
            MenuItem("Quit", self._handle_quit),
        )
        return Icon("Desktop App", self._create_icon_image(), "Desktop App", menu)

    def _create_icon_image(self) -> Any:
        if Image is None or ImageDraw is None:
            raise RuntimeError("Pillow unavailable")

        try:
            icon_path = Path(__file__).resolve().parents[3] / "assets" / "icon.png"
            if icon_path.exists():
                return Image.open(icon_path)
        except Exception as exc:
            logger.warning("[TRAY] Failed to load tray icon asset: %s", exc)

        img = Image.new("RGB", (64, 64), color="#2C2F33")
        draw = ImageDraw.Draw(img)
        draw.rectangle([22, 15, 42, 35], fill="#7289DA")
        draw.ellipse([22, 30, 42, 45], fill="#7289DA")
        return img

    def _handle_status_click(self, icon: object, item: object) -> None:
        if self._on_status_click:
            self._on_status_click()
        elif self._config.discord.bot_url and self._config.discord.member_id:
            logger.info("Connected to Discord: %s", self._config.discord.bot_url)
            logger.info("User ID: %s", self._config.discord.member_id)
        else:
            logger.warning("Discord is not fully configured")

    def _handle_configure(self, icon: object, item: object) -> None:
        if self._on_configure:
            self._on_configure()
        else:
            logger.warning("Settings are unavailable")

    def _handle_quit(self, icon: object, item: object) -> None:
        if self._on_quit:
            self._on_quit()
        else:
            logger.warning("[TRAY] Quit requested without a configured quit handler; hiding tray.")
            self.hide()


def create_system_tray_icon(config: DesktopAppConfig) -> SystemTrayIconAdapter:
    """Create the most appropriate tray adapter for the environment."""
    if _pystray_available:
        return PySystemTrayIcon(config)
    return NullSystemTrayIcon()


def is_system_tray_available() -> bool:
    """Expose pystray availability for status reporting."""
    return _pystray_available
