"""Shared routing helpers for selecting TTS delivery engines."""

from __future__ import annotations

import logging
from typing import Iterable, Protocol


class TTSDeliveryEngine(Protocol):
    """Contract for Desktop App delivery engines used by the fallback chain."""

    def speak(self, text: str) -> bool:
        """Speak the provided text."""

    def is_available(self) -> bool:
        """Return whether the engine can be used."""


def build_tts_engine_chain(
    preferred_engine: str,
    *,
    discord_engine: TTSDeliveryEngine | None = None,
    local_engine: TTSDeliveryEngine | None = None,
) -> list[TTSDeliveryEngine]:
    """Order available TTS engines based on the preferred configuration."""
    candidates = {
        "discord": discord_engine,
        "pyttsx3": local_engine,
    }

    if preferred_engine == "pyttsx3":
        engine_order = ("pyttsx3", "discord")
    else:
        engine_order = ("discord", "pyttsx3")

    ordered = [candidates[name] for name in engine_order if candidates[name] is not None]
    return ordered


class TTSFallbackChain:
    """Try TTS engines in order until one succeeds."""

    def __init__(self, engines: Iterable[TTSDeliveryEngine], logger: logging.Logger | None = None):
        self._engines = list(engines)
        self._logger = logger or logging.getLogger(__name__)
        self._last_error_message: str | None = None

    def speak(self, text: str) -> bool:
        """Try engines in order until one succeeds."""
        self._last_error_message = None

        for engine in self._engines:
            if engine.is_available():
                if engine.speak(text):
                    self._last_error_message = None
                    return True
                self._last_error_message = self._read_engine_error(engine)
                self._logger.warning(f"[TTS] Engine {engine.__class__.__name__} falhou, tentando próximo...")

        if self._last_error_message is None:
            self._last_error_message = "Nenhum engine TTS disponivel"
        self._logger.error("[TTS] Todos os engines falharam")
        return False

    def is_available(self) -> bool:
        """Check if any engine in the chain is available."""
        return any(engine.is_available() for engine in self._engines)

    def get_last_error_message(self) -> str | None:
        """Return the last available failure reason from the fallback chain."""
        return self._last_error_message

    @staticmethod
    def _read_engine_error(engine: TTSDeliveryEngine) -> str | None:
        """Read an optional human-friendly error message from an engine."""
        reader = getattr(engine, "get_last_error_message", None)
        if not callable(reader):
            return None

        try:
            return reader()
        except Exception:
            return None
