"""Configuration repository implementation."""
from typing import Optional

from src.core.entities import TTSConfig
from src.core.interfaces import IConfigRepository


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
        self._guild_configs: dict[int, TTSConfig] = {}
        self._user_configs: dict[tuple[int, int], TTSConfig] = {}
    
    def get_config(self, guild_id: Optional[int] = None, user_id: Optional[int] = None) -> TTSConfig:
        """Get resolved TTS configuration for a guild/user scope or the global default.
        
        Args:
            guild_id: Guild ID or None for default
             
        Returns:
            TTSConfig for the guild or default
        """
        if guild_id and user_id and (guild_id, user_id) in self._user_configs:
            return self._user_configs[(guild_id, user_id)]

        if guild_id and guild_id in self._guild_configs:
            return self._guild_configs[guild_id]
        
        # Return copy to avoid external modification
        return TTSConfig(
            engine=self._default_config.engine,
            language=self._default_config.language,
            voice_id=self._default_config.voice_id,
            rate=self._default_config.rate
        )

    async def load_config_async(self, guild_id: Optional[int] = None, user_id: Optional[int] = None) -> TTSConfig:
        """Load configuration asynchronously using the in-memory state."""
        return self.get_config(guild_id, user_id=user_id)
    
    def set_config(self, guild_id: int, config: TTSConfig, user_id: Optional[int] = None) -> None:
        """Set TTS configuration for a specific guild or guild/user scope.
        
        Args:
            guild_id: Guild ID
            config: New configuration
        """
        target = TTSConfig(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
            rate=config.rate
        )
        if user_id is not None:
            self._user_configs[(guild_id, user_id)] = target
            return

        self._guild_configs[guild_id] = target

    async def save_config_async(self, guild_id: int, config: TTSConfig, user_id: Optional[int] = None) -> bool:
        """Persist configuration asynchronously using the in-memory state."""
        self.set_config(guild_id, config, user_id=user_id)
        return True

    async def delete_config_async(self, guild_id: int, user_id: Optional[int] = None) -> bool:
        if user_id is not None:
            self._user_configs.pop((guild_id, user_id), None)
            return True
        self._guild_configs.pop(guild_id, None)
        return True

    def get_effective_scope(self, guild_id: Optional[int] = None, user_id: Optional[int] = None) -> str:
        if guild_id and user_id and (guild_id, user_id) in self._user_configs:
            return "user"
        if guild_id and guild_id in self._guild_configs:
            return "guild"
        return "default"
