"""Shared helpers for configuring pyttsx3-based engines."""

from __future__ import annotations

import logging
import platform
from typing import Protocol

from src.core.entities import TTSConfig


class Pyttsx3VoiceLike(Protocol):
    """Contract for pyttsx3 voice metadata used by shared helpers."""

    id: str
    name: str


class Pyttsx3EngineLike(Protocol):
    """Contract for pyttsx3 engine operations used by shared helpers."""

    def getProperty(self, name: str) -> object:
        """Read a pyttsx3 property."""
        ...

    def setProperty(self, name: str, value: object) -> None:
        """Set a pyttsx3 property."""
        ...

    def say(self, text: str) -> None:
        """Queue text to speak."""
        ...

    def runAndWait(self) -> None:
        """Run queued speech synchronously."""
        ...


def _normalize_voice_token(value: str) -> str:
    return value.strip().lower()


def _voice_matches(voice: Pyttsx3VoiceLike, requested: str) -> bool:
    normalized = _normalize_voice_token(requested)
    if not normalized:
        return False

    voice_id = getattr(voice, "id", "") or ""
    voice_name = getattr(voice, "name", "") or ""
    candidates = {
        _normalize_voice_token(voice_id),
        _normalize_voice_token(voice_name),
        _normalize_voice_token(voice_id.split("\\")[-1]),
    }
    return any(normalized in candidate for candidate in candidates if candidate)


def list_pyttsx3_voices(logger: logging.Logger | None = None) -> list[Pyttsx3VoiceLike]:
    """Return installed pyttsx3 voices, or an empty list when unavailable."""
    active_logger = logger or logging.getLogger(__name__)

    try:
        import pyttsx3

        driver_name = "sapi5" if platform.system() == "Windows" else None
        engine = pyttsx3.init(driverName=driver_name) if driver_name else pyttsx3.init()
        return list(engine.getProperty("voices") or [])
    except Exception as exc:
        active_logger.warning("Could not enumerate pyttsx3 voices: %s", exc)
        return []


def configure_pyttsx3_engine(
    engine: Pyttsx3EngineLike,
    config: TTSConfig,
    logger: logging.Logger | None = None,
) -> None:
    """Apply the shared voice and rate configuration to a pyttsx3 engine."""
    active_logger = logger or logging.getLogger(__name__)
    engine.setProperty("rate", config.rate)

    if not config.voice_id:
        return

    try:
        voices = engine.getProperty("voices")
    except Exception as exc:
        active_logger.warning(f"Could not enumerate voices: {exc}")
        return

    for voice in voices:
        if _voice_matches(voice, config.voice_id):
            engine.setProperty("voice", voice.id)
            return

    active_logger.warning(f"Voice '{config.voice_id}' not found, using default")
