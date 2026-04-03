"""Shared execution services for TTS flows."""

from __future__ import annotations

from src.application.tts_text import prepare_tts_text

TTS_EXECUTION_RESULT_OK = "ok"
TTS_EXECUTION_RESULT_MISSING_TEXT = "missing_text"
TTS_EXECUTION_RESULT_FAILED = "failed"


class SpeakTextExecutionUseCase:
    """Execute Desktop App TTS and return a structured result payload."""

    def __init__(self, tts_service: object):
        self._tts_service = tts_service

    def execute(self, text: str | None) -> dict:
        """Execute a text-to-speech request and return a neutral result payload."""
        prepared_text = prepare_tts_text(text)
        if not prepared_text:
            return {
                "success": False,
                "code": TTS_EXECUTION_RESULT_MISSING_TEXT,
            }

        success = self._tts_service.speak_text(text)
        if success:
            return {
                "success": True,
                "code": TTS_EXECUTION_RESULT_OK,
            }

        return {
            "success": False,
            "code": TTS_EXECUTION_RESULT_FAILED,
        }

    def is_available(self) -> bool:
        """Return whether the underlying TTS service is available."""
        return self._tts_service.is_available()

    def get_status_info(self) -> dict:
        """Expose status info from the underlying TTS service."""
        return self._tts_service.get_status_info()
