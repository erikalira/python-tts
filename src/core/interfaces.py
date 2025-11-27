"""Interfaces (abstract base classes) following Dependency Inversion Principle."""
from abc import ABC, abstractmethod
from typing import Optional
from .entities import TTSRequest, TTSConfig, AudioFile


class ITTSEngine(ABC):
    """Interface for text-to-speech engines."""
    
    @abstractmethod
    async def generate_audio(self, text: str, config: TTSConfig) -> AudioFile:
        """Generate audio file from text.
        
        Args:
            text: Text to convert to speech
            config: TTS configuration
            
        Returns:
            AudioFile object with path to generated audio
        """
        pass


class IVoiceChannel(ABC):
    """Interface for voice channel operations."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the voice channel."""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from the voice channel."""
        pass
    
    @abstractmethod
    async def play_audio(self, audio: AudioFile) -> None:
        """Play audio in the voice channel.
        
        Args:
            audio: AudioFile to play
        """
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to voice channel."""
        pass


class IVoiceChannelRepository(ABC):
    """Interface for finding voice channels."""
    
    @abstractmethod
    async def find_connected_channel(self) -> Optional[IVoiceChannel]:
        """Find any voice channel where bot is already connected."""
        pass
    
    @abstractmethod
    async def find_by_member_id(self, member_id: int) -> Optional[IVoiceChannel]:
        """Find voice channel where member is connected."""
        pass
    
    @abstractmethod
    async def find_by_channel_id(self, channel_id: int) -> Optional[IVoiceChannel]:
        """Find voice channel by ID."""
        pass
    
    @abstractmethod
    async def find_by_guild_id(self, guild_id: int) -> Optional[IVoiceChannel]:
        """Find first available voice channel in guild."""
        pass


class IConfigRepository(ABC):
    """Interface for configuration management."""
    
    @abstractmethod
    def get_config(self, user_id: Optional[int] = None) -> TTSConfig:
        """Get TTS configuration for user or global default."""
        pass
    
    @abstractmethod
    def set_config(self, user_id: int, config: TTSConfig) -> None:
        """Set TTS configuration for a specific user."""
        pass


class IInputListener(ABC):
    """Interface for input listening (keyboard, etc)."""
    
    @abstractmethod
    def start(self) -> None:
        """Start listening for input."""
        pass
    
    @abstractmethod
    def stop(self) -> None:
        """Stop listening for input."""
        pass
