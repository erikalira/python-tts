"""Shared result contracts for Desktop App runtime flows."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DesktopConfigurationSaveResult:
    """Structured result for Desktop App configuration saves from the main window."""

    success: bool
    message: str
