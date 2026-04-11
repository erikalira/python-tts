"""Shared execution services for TTS flows."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from src.application.tts_text import prepare_tts_text

TTS_EXECUTION_RESULT_OK = "ok"
TTS_EXECUTION_RESULT_MISSING_TEXT = "missing_text"
TTS_EXECUTION_RESULT_FAILED = "failed"


@dataclass(frozen=True)
class TTSExecutionResult:
    """Structured result for Desktop App TTS execution."""

    success: bool
    code: str
    message: str | None = None


class DesktopTTSExecutionPort(Protocol):
    """Port for Desktop App TTS execution and status reporting."""

    def speak_text(self, text: str) -> bool:
        """Execute speech for the provided normalized text."""

    def is_available(self) -> bool:
        """Return whether the underlying TTS flow is available."""

    def get_status_info(self) -> dict[str, Any]:
        """Return runtime status details for the Desktop App."""

    def get_last_error_message(self) -> str | None:
        """Return the latest execution error when available."""


class SpeakTextExecutionUseCase:
    """Execute Desktop App TTS through an explicit Desktop App port."""

    def __init__(self, tts_service: DesktopTTSExecutionPort):
        self._tts_service = tts_service

    def execute(self, text: str | None) -> TTSExecutionResult:
        """Execute a text-to-speech request and return a neutral result payload."""
        prepared_text = prepare_tts_text(text)
        if not prepared_text:
            return TTSExecutionResult(
                success=False,
                code=TTS_EXECUTION_RESULT_MISSING_TEXT,
            )

        success = self._tts_service.speak_text(prepared_text)
        if success:
            return TTSExecutionResult(
                success=True,
                code=TTS_EXECUTION_RESULT_OK,
            )

        error_message = self._tts_service.get_last_error_message()

        return TTSExecutionResult(
            success=False,
            code=TTS_EXECUTION_RESULT_FAILED,
            message=error_message or "Falha ao reproduzir o texto",
        )

    def is_available(self) -> bool:
        """Return whether the underlying TTS service is available."""
        return self._tts_service.is_available()

    def get_status_info(self) -> dict:
        """Expose status info from the underlying TTS service."""
        return self._tts_service.get_status_info()
