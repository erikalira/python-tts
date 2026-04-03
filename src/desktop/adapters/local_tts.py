#!/usr/bin/env python3
"""Local text-to-speech adapters for Desktop App services."""

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

    def create_engine(self) -> object:
        """Create a pyttsx3 engine instance."""
        if pyttsx3 is None:
            raise RuntimeError("pyttsx3 unavailable")
        return pyttsx3.init()


def is_pyttsx3_available() -> bool:
    """Expose pyttsx3 availability for status reporting."""
    return _pyttsx3_available and pyttsx3 is not None
