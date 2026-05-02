"""Infrastructure helpers for cleaning up generated audio files."""

from __future__ import annotations

import os
from contextlib import suppress

from src.core.entities import AudioFile
from src.core.interfaces import IAudioFileCleanup


class FileAudioCleanup(IAudioFileCleanup):
    """Delete temporary audio files from disk."""

    async def cleanup(self, audio: AudioFile) -> None:
        with suppress(OSError):
            os.unlink(audio.path)
