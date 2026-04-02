"""Shared routing helpers for selecting TTS delivery engines."""

from __future__ import annotations

import logging
from typing import Iterable


def build_tts_engine_chain(
    preferred_engine: str,
    *,
    discord_engine: object | None = None,
    local_engine: object | None = None,
) -> list[object]:
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

    def __init__(self, engines: Iterable[object], logger: logging.Logger | None = None):
        self._engines = list(engines)
        self._logger = logger or logging.getLogger(__name__)

    def speak(self, text: str) -> bool:
        """Try engines in order until one succeeds."""
        for engine in self._engines:
            if engine.is_available():
                if engine.speak(text):
                    return True
                self._logger.warning(f"[TTS] Engine {engine.__class__.__name__} falhou, tentando próximo...")

        self._logger.error("[TTS] Todos os engines falharam")
        return False

    def is_available(self) -> bool:
        """Check if any engine in the chain is available."""
        return any(engine.is_available() for engine in self._engines)
