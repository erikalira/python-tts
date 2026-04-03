"""Desktop App runtime helpers for TTS execution and user feedback."""

from __future__ import annotations

import logging
import threading
from typing import Callable, Optional

from src.application.tts_execution import (
    TTS_EXECUTION_RESULT_FAILED,
    TTS_EXECUTION_RESULT_MISSING_TEXT,
    TTS_EXECUTION_RESULT_OK,
    SpeakTextExecutionUseCase,
)

from ..adapters.keyboard_backend import KeyboardHookBackend
from ..services.hotkey_services import HotkeyEvent
from ..services.notification_services import SystemTrayService
from ..services.tts_services import DesktopAppTTSService, KeyboardCleanupService

logger = logging.getLogger(__name__)


class DesktopAppTTSResultPresenter:
    """Translate structured TTS execution results into desktop notifications."""

    def __init__(self, notification_service: SystemTrayService):
        self._notification_service = notification_service

    def show_processing(self, text: str) -> None:
        """Show a processing notification for captured text."""
        self._notification_service.notify_info(
            "Desktop App",
            f"Processando: '{text[:50]}{'...' if len(text) > 50 else ''}'",
        )

    def present(self, result: dict) -> None:
        """Show user-facing feedback after TTS execution completes."""
        code = result.get("code")
        if code == TTS_EXECUTION_RESULT_OK:
            self._notification_service.notify_success(
                "Desktop App", "Texto reproduzido com sucesso"
            )
            return

        if code == TTS_EXECUTION_RESULT_MISSING_TEXT:
            self._notification_service.notify_error(
                "Desktop App", "Nenhum texto valido foi capturado"
            )
            return

        if code == TTS_EXECUTION_RESULT_FAILED:
            self._notification_service.notify_error(
                "Desktop App", "Falha ao reproduzir o texto"
            )
            return

        self._notification_service.notify_error(
            "Desktop App", "Falha inesperada ao processar TTS"
        )


class DesktopAppTTSProcessor:
    """Coordinate execution threading and keyboard cleanup for the Desktop App."""

    def __init__(
        self,
        tts_service: Optional[DesktopAppTTSService] = None,
        cleanup_service: Optional[KeyboardCleanupService] = None,
        execution_service: Optional[SpeakTextExecutionUseCase] = None,
    ):
        if cleanup_service is None:
            raise ValueError(
                "DesktopAppTTSProcessor requires explicit tts_service and cleanup_service"
            )
        if execution_service is None:
            if tts_service is None:
                raise ValueError(
                    "DesktopAppTTSProcessor requires explicit tts_service and cleanup_service"
                )
            execution_service = SpeakTextExecutionUseCase(tts_service)
        self._execution_service = execution_service
        self._cleanup_service = cleanup_service

    def process_text(
        self,
        text: str,
        cleanup_count: int = 0,
        on_complete: Optional[Callable[[dict], None]] = None,
    ) -> None:
        """Process text for TTS and perform cleanup in a separate thread."""

        def _process() -> None:
            result = self._execution_service.execute(text)

            if result.get("success") and cleanup_count > 0:
                self._cleanup_service.cleanup_typed_text(cleanup_count)

            if on_complete is not None:
                on_complete(result)

        threading.Thread(target=_process, daemon=True).start()

    def is_processing(self) -> bool:
        """Check if keyboard events are currently suppressed by cleanup."""
        return self._cleanup_service.is_suppressing_events()

    def get_service_status(self) -> dict:
        """Expose execution and engine availability for status views."""
        return {
            "tts_available": self._execution_service.is_available(),
            "engines_info": self._execution_service.get_status_info(),
        }


class DesktopAppHotkeyHandler:
    """Hotkey handler that integrates captured text with TTS processing."""

    def __init__(
        self,
        tts_processor: DesktopAppTTSProcessor,
        result_presenter: DesktopAppTTSResultPresenter,
    ):
        self._tts_processor = tts_processor
        self._result_presenter = result_presenter

    def handle_text_captured(self, event: HotkeyEvent) -> None:
        """Handle when text is captured between hotkey triggers."""
        if not event.text:
            return

        logger.info("[DESKTOP_APP] Texto capturado pelo hotkey handler")
        self._result_presenter.show_processing(event.text)
        self._tts_processor.process_text(
            event.text,
            event.character_count,
            on_complete=self._result_presenter.present,
        )


def create_default_cleanup_service() -> KeyboardCleanupService:
    """Build the default keyboard cleanup service for the Desktop App."""
    return KeyboardCleanupService(keyboard_backend=KeyboardHookBackend())


TTSProcessor = DesktopAppTTSProcessor
StandaloneTTSResultPresenter = DesktopAppTTSResultPresenter
StandaloneHotkeyHandler = DesktopAppHotkeyHandler
