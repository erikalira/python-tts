"""Standalone service modules.

Avoid eager imports here so callers can import submodules without triggering
optional GUI or system-tray backends during package initialization.
"""

__all__: list[str] = []
