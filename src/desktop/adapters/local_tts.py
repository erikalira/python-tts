#!/usr/bin/env python3
"""Local text-to-speech adapters for Desktop App services."""

import logging

from src.core.entities import TTSConfig
from src.infrastructure.tts.pyttsx3_support import Pyttsx3EngineLike, configure_pyttsx3_engine

try:
    import pyttsx3
    _pyttsx3_available = True
except ImportError:
    pyttsx3 = None
    _pyttsx3_available = False


class Pyttsx3Adapter:
    """Thin adapter around pyttsx3 initialization."""

    def is_available(self) -> bool:
        """Return whether pyttsx3 is installed."""
        return _pyttsx3_available and pyttsx3 is not None

    def create_engine(self) -> Pyttsx3EngineLike:
        """Create a pyttsx3 engine instance."""
        if pyttsx3 is None:
            raise RuntimeError("pyttsx3 unavailable")
        return pyttsx3.init()

    def create_configured_engine(self, config: TTSConfig, logger: logging.Logger) -> Pyttsx3EngineLike:
        """Create and configure a pyttsx3 engine instance."""
        engine = self.create_engine()
        configure_pyttsx3_engine(engine, config, logger)
        return engine


def is_pyttsx3_available() -> bool:
    """Expose pyttsx3 availability for status reporting."""
    return _pyttsx3_available and pyttsx3 is not None
