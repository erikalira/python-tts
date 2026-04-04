"""Infrastructure helpers for cleaning up generated audio files."""

from __future__ import annotations

import os

from src.core.entities import AudioFile
from src.core.interfaces import IAudioFileCleanup


class FileAudioCleanup(IAudioFileCleanup):
    """Delete temporary audio files from disk."""

    async def cleanup(self, audio: AudioFile) -> None:
        try:
            os.unlink(audio.path)
        except OSError:
            pass
