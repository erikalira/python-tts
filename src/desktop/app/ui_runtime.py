"""UI runtime coordination for the Desktop App."""

from __future__ import annotations

import logging
import queue
from typing import Optional, Protocol
from collections.abc import Callable

from src.application.dto import (
    DesktopAppRuntimeStatusDTO,
    DesktopBotActionResultDTO,
    DesktopBotVoiceContextResultDTO,
    DesktopConfigurationSaveResultDTO,
)
from ..config.desktop_config import DesktopAppConfig
from ..gui.main_window import DesktopAppMainWindow

logger = logging.getLogger(__name__)


class NotificationInfoPort(Protocol):
    """Contract needed to show tray status notifications."""

    def notify_info(self, title: str, message: str) -> None:
        """Show an informational notification."""


class HotkeyManagerLike(Protocol):
    """Contract needed for configure flows triggered from the tray."""

    def is_active(self) -> bool:
        """Return whether hotkeys are active."""
        ...

    def stop(self) -> None:
        """Pause hotkeys."""

    def start(self) -> bool:
        """Resume hotkeys."""
        ...


class NotificationFeedbackPort(Protocol):
    """Contract used to show configuration feedback."""

    def notify_error(self, title: str, message: str) -> None:
        """Show an error notification."""

    def notify_success(self, title: str, message: str) -> None:
        """Show a success notification."""


class ConfigurationCoordinatorLike(Protocol):
    """Contract for the tray-triggered configuration flow."""

    def reconfigure(
        self,
        current_config: DesktopAppConfig,
        hotkeys_were_active: bool,
        resume_hotkeys: Callable[[], None],
        notify_error: Optional[Callable[[str, str], None]] = None,
        notify_success: Optional[Callable[[str, str], None]] = None,
        are_hotkeys_active: Optional[Callable[[], bool]] = None,
    ) -> tuple[Optional[DesktopAppConfig], bool]:
        """Run the configuration flow and return the updated config."""
        ...


class DesktopAppUIRuntimeCoordinator:
    """Own Desktop App window state, queued UI actions, and tray-triggered UI flows."""

    def __init__(self):
        self._main_loop_actions: "queue.Queue[Callable[[], None]]" = queue.Queue()
        self._main_window: Optional[DesktopAppMainWindow] = None

    @property
    def action_queue(self) -> "queue.Queue[Callable[[], None]]":
        return self._main_loop_actions

    @property
    def main_window(self) -> Optional[DesktopAppMainWindow]:
        return self._main_window

    def show_main_window(
        self,
        *,
        config: DesktopAppConfig,
        on_save: Callable[[DesktopAppConfig], DesktopConfigurationSaveResultDTO],
        on_test_connection: Callable[[DesktopAppConfig], DesktopBotActionResultDTO],
        on_send_test: Callable[[DesktopAppConfig], DesktopBotActionResultDTO],
        on_refresh_voice_context: Callable[[DesktopAppConfig], DesktopBotVoiceContextResultDTO],
    ) -> None:
        """Create and show the main Desktop App window."""
        self._main_window = DesktopAppMainWindow(
            config,
            on_save=on_save,
            on_test_connection=on_test_connection,
            on_send_test=on_send_test,
            on_refresh_voice_context=on_refresh_voice_context,
            on_process_ui_actions=self.drain_queued_actions,
        )
        self._main_window.show()

    def queue(self, action: Callable[[], None]) -> None:
        """Queue a UI action to run on the main thread."""
        self._main_loop_actions.put(action)

    def show_status(
        self,
        *,
        get_status: Callable[[], DesktopAppRuntimeStatusDTO],
        notification_service: NotificationInfoPort | None,
    ) -> None:
        """Show current app status via the main window or tray notifications."""
        if self._main_window:
            self._main_window.focus()
            self._main_window.push_log("Main window brought to front from tray")
            return

        status = get_status()
        mode = "Discord" if status.discord_configured else "Local"
        hotkeys = "active" if status.hotkey_active else "inactive"
        tts = "available" if status.tts_available else "unavailable"
        summary = f"{mode} mode | Hotkeys {hotkeys} | TTS {tts}"
        logger.info("[DESKTOP_APP] Status requested: %s", summary)
        if notification_service:
            notification_service.notify_info("Desktop App", summary)

    def handle_configure(
        self,
        *,
        ensure_action_coordinators: Callable[[], None],
        hotkey_manager: HotkeyManagerLike | None,
        get_configuration_coordinator: Callable[[], ConfigurationCoordinatorLike | None],
        current_config: DesktopAppConfig,
        notification_service: NotificationFeedbackPort | None,
    ) -> tuple[Optional[DesktopAppConfig], bool]:
        """Handle configure requests from tray or fallback UI flow."""
        if self._main_window:
            self._main_window.focus()
            self._main_window.push_log("Configuration action requested from tray")
            return None, False

        logger.info("[DESKTOP_APP] Opening settings...")
        ensure_action_coordinators()
        configuration_coordinator = get_configuration_coordinator()

        active_hotkey_manager = hotkey_manager
        hotkeys_were_active = active_hotkey_manager is not None and active_hotkey_manager.is_active()
        if active_hotkey_manager is not None and hotkeys_were_active:
            active_hotkey_manager.stop()

        if configuration_coordinator is None:
            logger.error("[DESKTOP_APP] Configuration coordinator is unavailable")
            return None, False

        return configuration_coordinator.reconfigure(
            current_config=current_config,
            hotkeys_were_active=hotkeys_were_active,
            resume_hotkeys=lambda: self._resume_hotkeys(hotkey_manager),
            notify_error=notification_service.notify_error if notification_service else None,
            notify_success=notification_service.notify_success if notification_service else None,
            are_hotkeys_active=hotkey_manager.is_active if hotkey_manager else None,
        )

    @staticmethod
    def _resume_hotkeys(hotkey_manager: HotkeyManagerLike | None) -> None:
        if hotkey_manager is not None:
            hotkey_manager.start()

    def drain_queued_actions(self) -> None:
        """Run all queued UI actions without blocking the Tk main loop."""
        while True:
            try:
                action = self._main_loop_actions.get_nowait()
            except queue.Empty:
                return
            action()
