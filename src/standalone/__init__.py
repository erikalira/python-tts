"""Standalone runtime package for the Windows hotkey app.

This package intentionally avoids eager imports so entrypoints can be imported
without immediately initializing GUI or system-tray backends.
"""

__all__: list[str] = []
