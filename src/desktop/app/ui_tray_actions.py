"""UI and tray action coordination for the Desktop App runtime."""

from __future__ import annotations

import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class DesktopAppUIActionsCoordinator:
    """Handle UI and tray actions without owning the whole runtime lifecycle."""

    def show_status(
        self,
        *,
        main_window: object,
        get_status: Callable[[], dict],
        notification_service: object,
    ) -> None:
        """Show current app status via the main window or tray notifications."""
        if main_window:
            main_window.focus()
            main_window.push_log("Janela principal trazida para frente via tray")
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
        main_window: object,
        ensure_action_coordinators: Callable[[], None],
        hotkey_manager: object,
        get_configuration_coordinator: Callable[[], object],
        current_config: object,
        notification_service: object,
    ) -> tuple[Optional[object], bool]:
        """Handle configure requests from tray or fallback UI flow."""
        if main_window:
            main_window.focus()
            main_window.push_log("Acao de configuracao solicitada via tray")
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
