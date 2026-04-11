"""Configuration repository implementation."""
from typing import Optional, Dict
from src.core.interfaces import IConfigRepository
from src.core.entities import TTSConfig


class InMemoryConfigRepository(IConfigRepository):
    """In-memory configuration storage.
    
    Follows Single Responsibility: only manages configuration storage.
    """
    
    def __init__(self, default_config: TTSConfig):
        """Initialize repository with default configuration.
        
        Args:
            default_config: Default TTS configuration
        """
        self._default_config = default_config
        self._guild_configs: Dict[int, TTSConfig] = {}
    
    def get_config(self, guild_id: Optional[int] = None) -> TTSConfig:
        """Get TTS configuration for a guild or the global default.
        
        Args:
            guild_id: Guild ID or None for default
             
        Returns:
            TTSConfig for the guild or default
        """
        if guild_id and guild_id in self._guild_configs:
            return self._guild_configs[guild_id]
        
        # Return copy to avoid external modification
        return TTSConfig(
            engine=self._default_config.engine,
            language=self._default_config.language,
            voice_id=self._default_config.voice_id,
            rate=self._default_config.rate
        )

    async def load_config_async(self, guild_id: Optional[int] = None) -> TTSConfig:
        """Load configuration asynchronously using the in-memory state."""
        return self.get_config(guild_id)
    
    def set_config(self, guild_id: int, config: TTSConfig) -> None:
        """Set TTS configuration for a specific guild.
        
        Args:
            guild_id: Guild ID
            config: New configuration
        """
        self._guild_configs[guild_id] = TTSConfig(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
            rate=config.rate
        )

    async def save_config_async(self, guild_id: int, config: TTSConfig) -> bool:
        """Persist configuration asynchronously using the in-memory state."""
        self.set_config(guild_id, config)
        return True
