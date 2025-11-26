"""Domain entities - pure business objects without external dependencies."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class TTSRequest:
    """Represents a text-to-speech request."""
    text: str
    channel_id: Optional[int] = None
    guild_id: Optional[int] = None
    member_id: Optional[int] = None


@dataclass
class TTSConfig:
    """TTS engine configuration."""
    engine: str = 'gtts'  # 'gtts' or 'pyttsx3'
    language: str = 'pt'
    voice_id: str = 'roa/pt-br'
    rate: int = 180


@dataclass
class AudioFile:
    """Represents an audio file path."""
    path: str
    
    def cleanup(self):
        """Clean up the audio file."""
        import os
        try:
            os.unlink(self.path)
        except Exception:
            pass
