"""Shared Desktop App TTS orchestration helpers."""

from __future__ import annotations

import logging
from typing import Protocol

from src.application.dto import DesktopTTSStatusDTO

from .tts_routing import TTSFallbackChain, build_tts_engine_chain
from .tts_text import prepare_tts_text


class TTSEnginePort(Protocol):
    """Port for a synchronous TTS engine used by the Desktop App."""

    def speak(self, text: str) -> bool:
        """Speak the given text."""

    def is_available(self) -> bool:
        """Return whether the engine can be used."""

    def get_last_error_message(self) -> str | None:
        """Return the last human-readable engine error when available."""


class DesktopTTSStatusGateway(Protocol):
    """Port for status data needed by Desktop App TTS views."""

    def is_remote_available(self) -> bool:
        """Return whether the remote/Discord path is available."""

    def is_local_enabled(self) -> bool:
        """Return whether local TTS is enabled in configuration."""

    def is_local_available(self) -> bool:
        """Return whether the local TTS adapter is usable."""

    def is_local_dependency_installed(self) -> bool:
        """Return whether the local TTS dependency is installed."""

    def has_transport(self) -> bool:
        """Return whether the HTTP transport dependency is installed."""

    def has_bot_url(self) -> bool:
        """Return whether the bot URL is configured."""


class DesktopTTSFlowService:
    """Coordinate text preparation and engine fallback for Desktop App TTS."""

    def __init__(
        self,
        *,
        preferred_engine: str,
        discord_engine: TTSEnginePort | None,
        local_engine: TTSEnginePort | None,
        max_text_length: int | None,
        logger: logging.Logger | None = None,
    ):
        self._max_text_length = max_text_length
        self._logger = logger or logging.getLogger(__name__)
        self._engine = TTSFallbackChain(
            build_tts_engine_chain(
                preferred_engine,
                discord_engine=discord_engine,
                local_engine=local_engine,
            ),
            logger=self._logger,
        )

    def speak_text(self, text: str | None) -> bool:
        """Prepare and speak text using the configured fallback chain."""
        prepared_text = prepare_tts_text(text, self._max_text_length)
        if not prepared_text:
            return False

        normalized = (text or "").strip()
        if normalized and prepared_text != normalized and self._max_text_length:
            self._logger.warning("[TTS] Text truncated to %s characters", self._max_text_length)

        self._logger.info("[TTS] Processing text for synthesis")
        return self._engine.speak(prepared_text)

    def is_available(self) -> bool:
        """Return whether at least one configured TTS engine is available."""
        return self._engine.is_available()

    def get_last_error_message(self) -> str | None:
        """Expose the latest error captured by the fallback chain."""
        return self._engine.get_last_error_message()


class DesktopTTSStatusUseCase:
    """Build Desktop App status information for local/remote TTS availability."""

    def __init__(self, gateway: DesktopTTSStatusGateway):
        self._gateway = gateway

    def execute(self) -> DesktopTTSStatusDTO:
        """Return the typed TTS status for Desktop App runtime views."""
        return DesktopTTSStatusDTO(
            discord_available=self._gateway.is_remote_available(),
            local_tts_enabled=self._gateway.is_local_enabled(),
            local_available=self._gateway.is_local_available(),
            pyttsx3_installed=self._gateway.is_local_dependency_installed(),
            requests_installed=self._gateway.has_transport(),
            bot_url_configured=self._gateway.has_bot_url(),
        )
