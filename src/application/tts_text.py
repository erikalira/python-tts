"""Shared text preparation rules for TTS flows."""

from __future__ import annotations


def prepare_tts_text(text: str | None, max_length: int | None = None) -> str:
    """Normalize user text before it enters a TTS pipeline."""
    normalized = (text or "").strip()
    if not normalized:
        return ""

    if max_length is not None and max_length > 0:
        return normalized[:max_length]

    return normalized
