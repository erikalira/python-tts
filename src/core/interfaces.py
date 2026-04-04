"""Interfaces (abstract base classes) following Dependency Inversion Principle."""
from abc import ABC, abstractmethod
from typing import Optional
from .entities import TTSConfig, AudioFile, AudioQueueItem


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

    @abstractmethod
    def get_channel_id(self) -> int:
        """Get the channel ID."""
        pass

    @abstractmethod
    def get_channel_name(self) -> str:
        """Get the channel name."""
        pass

    @abstractmethod
    def get_guild_id(self) -> int:
        """Get the guild ID for the voice channel."""
        pass

    @abstractmethod
    def get_guild_name(self) -> str:
        """Get the guild name for the voice channel."""
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
    async def find_by_guild_id(self, guild_id: Optional[int]) -> Optional[IVoiceChannel]:
        """Find first available voice channel in guild."""
        pass


class IConfigRepository(ABC):
    """Interface for configuration management."""
    
    @abstractmethod
    def get_config(self, user_id: Optional[int] = None) -> TTSConfig:
        """Get TTS configuration for user or global default."""
        pass

    @abstractmethod
    async def load_config_async(self, user_id: Optional[int] = None) -> TTSConfig:
        """Load TTS configuration asynchronously for user or global default."""
        pass
    
    @abstractmethod
    def set_config(self, user_id: int, config: TTSConfig) -> None:
        """Set TTS configuration for a specific user."""
        pass

    @abstractmethod
    async def save_config_async(self, user_id: int, config: TTSConfig) -> bool:
        """Persist TTS configuration asynchronously for a specific user."""
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


class IAudioQueue(ABC):
    """Interface for managing audio queue per guild.
    
    Supports multiple users per server with FIFO queue processing.
    Separate queues per guild for multi-server support.
    """
    
    @abstractmethod
    async def enqueue(self, item: AudioQueueItem) -> Optional[str]:
        """Add item to queue for its guild.
        
        Args:
            item: AudioQueueItem to enqueue
            
        Returns:
            item_id: Unique identifier for the queued item, or None if rejected
        """
        pass
    
    @abstractmethod
    async def dequeue(self, guild_id: Optional[int]) -> Optional[AudioQueueItem]:
        """Remove and return next item from guild's queue.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            Next AudioQueueItem or None if queue empty
        """
        pass
    
    @abstractmethod
    async def peek_next(self, guild_id: Optional[int]) -> Optional[AudioQueueItem]:
        """Look at next item without removing it.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            Next AudioQueueItem or None if queue empty
        """
        pass
    
    @abstractmethod
    async def get_queue_status(self, guild_id: Optional[int]) -> dict:
        """Get current queue status for a guild.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            dict with 'size' (int) and 'items' (list of dicts)
        """
        pass
    
    @abstractmethod
    async def get_item_position(self, item_id: str) -> int:
        """Get position of specific item in any queue.
        
        Args:
            item_id: Item identifier to search for
            
        Returns:
            Position (0-indexed) or -1 if not found
        """
        pass
    
    @abstractmethod
    async def clear_completed(self, guild_id: Optional[int], older_than_seconds: int = 3600):
        """Remove completed/failed items older than threshold.
        
        Args:
            guild_id: Guild identifier
            older_than_seconds: Remove items older than this duration
        """
        pass


class IAudioFileCleanup(ABC):
    """Interface for cleaning up generated audio artifacts."""

    @abstractmethod
    async def cleanup(self, audio: AudioFile) -> None:
        """Delete or release generated audio resources."""
        pass
