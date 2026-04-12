"""Input DTO for voice-context queries."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VoiceContextQueryDTO:
    """Normalized input contract for current voice-context queries."""

    member_id: int | None = None
