"""Shared helpers for configuring pyttsx3-based engines."""

from __future__ import annotations

import logging

from src.core.entities import TTSConfig


def configure_pyttsx3_engine(engine: object, config: TTSConfig, logger: logging.Logger | None = None) -> None:
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
        if config.voice_id.lower() in voice.id.lower():
            engine.setProperty("voice", voice.id)
            return

    active_logger.warning(f"Voice '{config.voice_id}' not found, using default")
