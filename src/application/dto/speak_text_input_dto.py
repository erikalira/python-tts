"""Input DTO for speak-text use-case boundaries."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.entities import TTSConfig


@dataclass(frozen=True, slots=True)
class SpeakTextInputDTO:
    """Normalized input contract for speak text requests."""

    text: str
    channel_id: int | None = None
    guild_id: int | None = None
    member_id: int | None = None
    config_override: TTSConfig | None = None
