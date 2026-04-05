"""Infrastructure adapter for Discord voice runtime availability."""

from __future__ import annotations

from importlib.util import find_spec

from src.application.voice_runtime import VoiceRuntimeStatus
from src.infrastructure.discord.ffmpeg_runtime import has_ffmpeg_runtime


class DependencyVoiceRuntimeAvailability:
    """Check process-level dependencies required for Discord voice support."""

    def get_status(self) -> VoiceRuntimeStatus:
        return VoiceRuntimeStatus(
            ffmpeg_available=has_ffmpeg_runtime(),
            pynacl_installed=find_spec("nacl") is not None,
            davey_installed=find_spec("davey") is not None,
        )
