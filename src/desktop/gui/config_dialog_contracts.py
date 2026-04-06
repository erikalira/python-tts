"""Shared contracts for Desktop App configuration dialogs."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..config.desktop_config import DesktopAppConfig


class ConfigInterface(ABC):
    """Abstract interface for Desktop App configuration flows."""

    @abstractmethod
    def show_config(self, config: DesktopAppConfig) -> Optional[DesktopAppConfig]:
        """Show a configuration UI and return the updated config when accepted."""
