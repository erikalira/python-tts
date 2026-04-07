"""UI runtime coordination for the Desktop App."""

from __future__ import annotations

import logging
import queue
from typing import Callable, Optional

from src.application.desktop_bot import DesktopBotActionResult, DesktopBotVoiceContextResult
from ..config.desktop_config import DesktopAppConfig
from ..gui.main_window import DesktopAppMainWindow
from ..results import DesktopConfigurationSaveResult

logger = logging.getLogger(__name__)


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
        on_save: Callable[[DesktopAppConfig], DesktopConfigurationSaveResult],
        on_test_connection: Callable[[DesktopAppConfig], DesktopBotActionResult],
        on_send_test: Callable[[DesktopAppConfig], DesktopBotActionResult],
        on_refresh_voice_context: Callable[[DesktopAppConfig], DesktopBotVoiceContextResult],
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
        get_status: Callable[[], dict],
        notification_service: object,
    ) -> None:
        """Show current app status via the main window or tray notifications."""
        if self._main_window:
            self._main_window.focus()
            self._main_window.push_log("Janela principal trazida para frente via tray")
            return

        status = get_status()
        mode = "Discord" if status["discord_configured"] else "Local"
        hotkeys = "ativas" if status["hotkey_active"] else "inativas"
        tts = "disponivel" if status["tts_available"] else "indisponivel"
        summary = f"Modo {mode} | Hotkeys {hotkeys} | TTS {tts}"
        logger.info("[DESKTOP_APP] Status solicitado: %s", summary)
        if notification_service:
            notification_service.notify_info("Desktop App", summary)

    def handle_configure(
        self,
        *,
        ensure_action_coordinators: Callable[[], None],
        hotkey_manager: object,
        get_configuration_coordinator: Callable[[], object],
        current_config: object,
        notification_service: object,
    ) -> tuple[Optional[object], bool]:
        """Handle configure requests from tray or fallback UI flow."""
        if self._main_window:
            self._main_window.focus()
            self._main_window.push_log("Acao de configuracao solicitada via tray")
            return None, False

        logger.info("[DESKTOP_APP] Abrindo configuracoes...")
        ensure_action_coordinators()
        configuration_coordinator = get_configuration_coordinator()

        hotkeys_were_active = bool(hotkey_manager and hotkey_manager.is_active())
        if hotkeys_were_active:
            hotkey_manager.stop()

        if configuration_coordinator is None:
            logger.error("[DESKTOP_APP] Coordenador de configuracao indisponivel")
            return None, False

        return configuration_coordinator.reconfigure(
            current_config=current_config,
            hotkeys_were_active=hotkeys_were_active,
            pause_hotkeys=lambda: hotkey_manager.stop() if hotkey_manager else None,
            resume_hotkeys=lambda: hotkey_manager.start() if hotkey_manager else None,
            notify_error=notification_service.notify_error if notification_service else None,
            notify_success=notification_service.notify_success if notification_service else None,
            are_hotkeys_active=hotkey_manager.is_active if hotkey_manager else None,
        )

    def drain_queued_actions(self) -> None:
        """Run all queued UI actions without blocking the Tk main loop."""
        while True:
            try:
                action = self._main_loop_actions.get_nowait()
            except queue.Empty:
                return
            action()
