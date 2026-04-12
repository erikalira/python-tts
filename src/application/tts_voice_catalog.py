"""Application contracts for exposing user-selectable TTS voice options."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TTSVoiceOption:
    """A selectable voice option exposed to presentation layers."""

    key: str
    engine: str
    label: str
    language: str
    voice_id: str


class TTSCatalog(Protocol):
    """Port for listing and resolving user-selectable TTS voices."""

    def list_voice_options(self) -> list[TTSVoiceOption]:
        """Return available voice options."""

    def get_voice_option(self, key: str) -> TTSVoiceOption | None:
        """Resolve a selectable option by its stable key."""

    def find_voice_option(self, *, engine: str, language: str, voice_id: str) -> TTSVoiceOption | None:
        """Resolve the currently active configuration back to a catalog option."""

    def is_voice_available(self, *, engine: str, voice_id: str) -> bool:
        """Return whether the configured voice identifier resolves for the engine."""
