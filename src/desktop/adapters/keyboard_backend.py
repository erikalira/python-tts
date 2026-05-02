#!/usr/bin/env python3
"""Keyboard library adapters for Desktop App services."""

from collections.abc import Callable

try:
    import keyboard

    _keyboard_available = True
except ImportError:
    keyboard = None
    _keyboard_available = False


class KeyboardHookBackend:
    """Adapter around the optional keyboard library."""

    key_down_event = "down"

    def is_available(self) -> bool:
        """Return whether the keyboard backend is installed."""
        return _keyboard_available and keyboard is not None

    def hook(self, callback: Callable) -> None:
        """Register a keyboard event callback."""
        if keyboard is None:
            raise RuntimeError("keyboard backend unavailable")
        keyboard.hook(callback)

    def unhook_all(self) -> None:
        """Remove all registered keyboard callbacks."""
        if keyboard is None:
            return
        keyboard.unhook_all()

    def send_backspace(self) -> None:
        """Emit a backspace key event."""
        if keyboard is None:
            raise RuntimeError("keyboard backend unavailable")
        keyboard.send("backspace")


def is_keyboard_backend_available() -> bool:
    """Expose keyboard backend availability for status reporting."""
    return _keyboard_available and keyboard is not None
