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
        self._user_configs: Dict[int, TTSConfig] = {}
    
    def get_config(self, user_id: Optional[int] = None) -> TTSConfig:
        """Get TTS configuration for user or global default.
        
        Args:
            user_id: User ID or None for default
            
        Returns:
            TTSConfig for the user or default
        """
        if user_id and user_id in self._user_configs:
            return self._user_configs[user_id]
        
        # Return copy to avoid external modification
        return TTSConfig(
            engine=self._default_config.engine,
            language=self._default_config.language,
            voice_id=self._default_config.voice_id,
            rate=self._default_config.rate
        )
    
    def set_config(self, user_id: int, config: TTSConfig) -> None:
        """Set TTS configuration for a specific user.
        
        Args:
            user_id: User ID
            config: New configuration
        """
        self._user_configs[user_id] = TTSConfig(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
            rate=config.rate
        )
