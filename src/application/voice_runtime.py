"""Application contracts for Discord voice runtime availability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class VoiceRuntimeStatus:
    """Structured availability details for Discord voice support."""

    ffmpeg_available: bool
    pynacl_installed: bool
    davey_installed: bool

    @property
    def is_available(self) -> bool:
        """Return whether all required runtime dependencies are present."""
        return (
            self.ffmpeg_available
            and self.pynacl_installed
            and self.davey_installed
        )

    def missing_dependencies(self) -> list[str]:
        """Return the names of missing runtime dependencies."""
        missing: list[str] = []
        if not self.pynacl_installed:
            missing.append("PyNaCl")
        if not self.davey_installed:
            missing.append("davey")
        if not self.ffmpeg_available:
            missing.append("FFmpeg")
        return missing


class VoiceRuntimeAvailability(Protocol):
    """Port for checking whether Discord voice runtime support is available."""

    def get_status(self) -> VoiceRuntimeStatus:
        """Return the current runtime availability details."""
