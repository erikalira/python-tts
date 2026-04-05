"""FFmpeg runtime helpers for Discord voice support."""

from __future__ import annotations

import os
import shutil


def resolve_ffmpeg_executable() -> str | None:
    """Return the FFmpeg executable path from env or PATH."""
    configured_path = os.getenv("FFMPEG_PATH", "").strip()
    if configured_path:
        return configured_path
    return shutil.which("ffmpeg")


def has_ffmpeg_runtime() -> bool:
    """Return whether FFmpeg is available for the current process."""
    return resolve_ffmpeg_executable() is not None
