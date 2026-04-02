"""Shared execution services for TTS flows."""

from __future__ import annotations


class TTSExecutionService:
    """Execute a prepared TTS request through a provided service."""

    def __init__(self, tts_service: object):
        self._tts_service = tts_service

    def execute(self, text: str) -> bool:
        """Execute a text-to-speech request and return whether it succeeded."""
        return self._tts_service.speak_text(text)

    def is_available(self) -> bool:
        """Return whether the underlying TTS service is available."""
        return self._tts_service.is_available()

    def get_status_info(self) -> dict:
        """Expose status info from the underlying TTS service."""
        return self._tts_service.get_status_info()
