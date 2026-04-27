"""Lifecycle coordination for the Desktop App runtime."""

from __future__ import annotations

import logging
import queue
from threading import Event
from typing import Callable, Protocol, TypeVar

from src.application.dto import DesktopTTSServiceStatusDTO

logger = logging.getLogger(__name__)

ConfigT = TypeVar("ConfigT")


class DesktopTTSProcessorLike(Protocol):
    """Runtime contract for Desktop App TTS processors."""

    def get_service_status(self) -> DesktopTTSServiceStatusDTO:
        """Return the typed TTS status object."""


class HotkeyManagerLike(Protocol):
    """Runtime contract for Desktop App hotkey management."""

    def start(self) -> bool:
        ...

    def stop(self) -> None:
        ...

    def is_active(self) -> bool:
        ...


class NotificationServiceLike(Protocol):
    """Runtime contract for Desktop App notification and tray services."""

    def start(self) -> bool:
        ...

    def stop(self) -> None:
        ...

    def is_running(self) -> bool:
        ...

    def is_available(self) -> bool:
        ...


class DesktopAppLifecycleCoordinator:
    """Coordinate runtime startup, main-loop behavior, and shutdown."""

    def __init__(self, tkinter_available: bool):
        self._tkinter_available = tkinter_available

    def start_services(
        self,
        hotkey_manager: HotkeyManagerLike,
        notification_service: NotificationServiceLike,
    ) -> bool:
        """Start runtime services and return whether startup succeeded."""
        logger.info("[DESKTOP_APP] Starting services...")

        if not hotkey_manager.start():
            logger.error("[DESKTOP_APP] Failed to start hotkey monitoring")
            return False

        tray_started = notification_service.start()
        if not tray_started:
            logger.warning("[DESKTOP_APP] System tray is not available, running in console mode")

        logger.info("[DESKTOP_APP] All services started")
        return True

    def run_main_loop(
        self,
        *,
        show_main_window: Callable[[], None],
        notification_service: NotificationServiceLike,
        process_pending_ui_action: Callable[[float], None],
        is_running: Callable[[], bool],
        shutdown_requested: Event,
        console_wait_factory: Callable[[], object],
    ) -> None:
        """Run the appropriate main loop for the current environment."""
        if self._tkinter_available:
            show_main_window()
            return

        tray_running = notification_service.is_running()
        if tray_running:
            logger.info("[DESKTOP_APP] Executando com system tray em background...")
            while is_running() and not shutdown_requested.is_set():
                process_pending_ui_action(0.2)
            return

        logger.info("[DESKTOP_APP] Console mode active. Press Ctrl+C to exit...")
        wait_backend = console_wait_factory()
        if hasattr(wait_backend, "is_available") and wait_backend.is_available():
            try:
                import keyboard

                keyboard.wait()
                return
            except ImportError:
                pass
        input("Pressione Enter para sair...")

    def update_services_config(
        self,
        *,
        running: bool,
        config: ConfigT,
        hotkey_manager: HotkeyManagerLike | None,
        tts_processor: DesktopTTSProcessorLike | None,
        notification_service: NotificationServiceLike | None,
        tts_processor_factory: Callable[[ConfigT], DesktopTTSProcessorLike],
        notification_service_factory: Callable[[ConfigT], NotificationServiceLike],
        initialize_notification_service: Callable[[NotificationServiceLike], None],
        rebuild_hotkey_manager: Callable[[bool], None],
    ) -> tuple[DesktopTTSProcessorLike | None, NotificationServiceLike | None]:
        """Rebuild dependent services after a configuration change."""
        hotkeys_were_active = bool(hotkey_manager and hotkey_manager.is_active())
        if hotkeys_were_active:
            hotkey_manager.stop()

        if tts_processor:
            tts_processor = tts_processor_factory(config)

        if notification_service:
            tray_should_restart = running and notification_service.is_available()
            notification_service.stop()
            notification_service = notification_service_factory(config)
            initialize_notification_service(notification_service)
            if tray_should_restart:
                notification_service.start()

        rebuild_hotkey_manager(hotkeys_were_active)
        return tts_processor, notification_service

    def shutdown(
        self,
        *,
        running: bool,
        hotkey_manager: HotkeyManagerLike | None,
        notification_service: NotificationServiceLike | None,
        shutdown_requested: Event,
        main_window: object | None,
    ) -> bool:
        """Shutdown runtime services and return the new running flag."""
        logger.info("[DESKTOP_APP] Encerrando aplicacao...")
        shutdown_requested.set()

        if running:
            if hotkey_manager:
                hotkey_manager.stop()
            if notification_service:
                notification_service.stop()
            running = False

        main_window_root = getattr(main_window, "root", None)
        if main_window_root:
            try:
                main_window_root.quit()
            except Exception:
                logger.debug(
                    "[DESKTOP_APP] Failed to close main window loop",
                    exc_info=True,
                )

        logger.info("[DESKTOP_APP] Aplicacao encerrada")
        return running

    def process_pending_ui_action(
        self,
        *,
        action_queue: "queue.Queue[Callable[[], None]]",
        timeout: float,
    ) -> None:
        """Execute a queued UI action on the main thread."""
        try:
            action = action_queue.get(timeout=timeout)
        except queue.Empty:
            return
        action()
