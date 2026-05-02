"""Configuration storage with per-guild isolation and persistence."""
import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Optional, cast

from src.core.entities import TTSConfig
from src.core.interfaces import IConfigRepository

logger = logging.getLogger(__name__)


class IConfigStorage(ABC):
    """Abstract interface for configuration persistence."""

    @abstractmethod
    async def load(self, guild_id: int, user_id: Optional[int] = None) -> Optional[TTSConfig]:
        """Load configuration for a guild or guild/user scope.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            TTSConfig if found, None otherwise
        """

    @abstractmethod
    async def save(self, guild_id: int, config: TTSConfig, user_id: Optional[int] = None) -> bool:
        """Save configuration for a guild or guild/user scope.
        
        Args:
            guild_id: Guild identifier
            config: Configuration to save
            
        Returns:
            True if saved successfully
        """

    @abstractmethod
    async def delete(self, guild_id: int, user_id: Optional[int] = None) -> bool:
        """Delete configuration for a guild or guild/user scope.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            True if deleted successfully
        """


class JSONConfigStorage(IConfigStorage):
    """File-based storage using JSON for configuration.
    
    Stores guild configurations in isolated files:
    - configs/guild_{guild_id}.json
    
    Advantages:
    - No external dependencies (Redis, DB)
    - Survives bot restarts
    - Per-guild isolation
    - Easy debugging
    """

    def __init__(self, storage_dir: str = "configs"):
        """Initialize JSON storage.
        
        Args:
            storage_dir: Directory to store config files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        logger.info(f"[CONFIG_STORAGE] Initialized JSON storage at {self.storage_dir}")

    def _get_config_path(self, guild_id: int, user_id: Optional[int] = None) -> Path:
        """Get file path for guild config.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            Path to config file
        """
        if user_id is not None:
            return self.storage_dir / f"guild_{guild_id}_user_{user_id}.json"
        return self.storage_dir / f"guild_{guild_id}.json"

    def _parse_config_data(self, data: dict[str, Any]) -> TTSConfig:
        """Build TTSConfig from persisted JSON payload."""
        return TTSConfig(
            engine=str(data.get("engine", "gtts")),
            language=str(data.get("language", "pt")),
            voice_id=str(data.get("voice_id", "roa/pt-br")),
            rate=int(data.get("rate", 180)),
        )

    def load_sync(self, guild_id: int, user_id: Optional[int] = None) -> Optional[TTSConfig]:
        """Load configuration synchronously for cache-miss recovery paths."""
        config_path = self._get_config_path(guild_id, user_id=user_id)

        if not config_path.exists():
            logger.debug(f"[CONFIG_STORAGE] No config file for guild {guild_id}")
            return None

        try:
            with open(config_path) as f:
                data = json.load(f)
            if not isinstance(data, dict):
                raise ValueError("Config root must be an object")

            config = self._parse_config_data(data)
            logger.debug(f"[CONFIG_STORAGE] Loaded config synchronously for guild {guild_id}: {config.engine}")
            return config

        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"[CONFIG_STORAGE] Failed to load config for guild {guild_id}: {e}")
            return None

    async def load(self, guild_id: int, user_id: Optional[int] = None) -> Optional[TTSConfig]:
        """Load configuration for a guild from JSON file.

        Args:
            guild_id: Guild identifier

        Returns:
            TTSConfig if found and valid, None otherwise
        """
        return self.load_sync(guild_id, user_id=user_id)

    async def save(self, guild_id: int, config: TTSConfig, user_id: Optional[int] = None) -> bool:
        """Save configuration for a guild to JSON file.
        
        Args:
            guild_id: Guild identifier
            config: Configuration to save
            
        Returns:
            True if saved successfully
        """
        config_path = self._get_config_path(guild_id, user_id=user_id)

        try:
            data = {
                "guild_id": guild_id,
                "user_id": user_id,
                "engine": config.engine,
                "language": config.language,
                "voice_id": config.voice_id,
                "rate": config.rate,
            }

            with open(config_path, "w") as f:
                json.dump(data, f, indent=2)

            logger.info(f"[CONFIG_STORAGE] Saved config for guild {guild_id}")
            return True

        except Exception as e:
            logger.error(f"[CONFIG_STORAGE] Failed to save config for guild {guild_id}: {e}")
            return False

    async def delete(self, guild_id: int, user_id: Optional[int] = None) -> bool:
        """Delete configuration for a guild.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            True if deleted successfully
        """
        config_path = self._get_config_path(guild_id, user_id=user_id)

        try:
            if config_path.exists():
                config_path.unlink()
                logger.info(f"[CONFIG_STORAGE] Deleted config for guild {guild_id}")
            return True

        except Exception as e:
            logger.error(f"[CONFIG_STORAGE] Failed to delete config for guild {guild_id}: {e}")
            return False


class GuildConfigRepository(IConfigRepository):
    """Configuration repository with per-guild isolation and persistence.
    
    Uses dependency injection to support different storage backends:
    - JSONConfigStorage for file-based persistence
    - RedisConfigStorage (future) for distributed deployments
    
    Guarantees:
    - Each guild has isolated configuration
    - No data leakage between servers
    - Configurations persist across bot restarts
    - Fallback to defaults if storage unavailable
    """

    def __init__(self, default_config: TTSConfig, storage: IConfigStorage):
        """Initialize repository with storage backend.
        
        Args:
            default_config: Default configuration for new guilds
            storage: Storage backend for persistence
        """
        self._default_config = default_config
        self._storage = storage
        # In-memory cache for fast access
        self._cache: dict[int, TTSConfig] = {}
        self._user_cache: dict[tuple[int, int], TTSConfig] = {}
        logger.info("[CONFIG_REPO] Initialized per-guild configuration repository")

    def _clone_config(self, config: TTSConfig) -> TTSConfig:
        """Return an isolated copy so callers never mutate cache-owned state."""
        return TTSConfig(
            engine=config.engine,
            language=config.language,
            voice_id=config.voice_id,
            rate=config.rate,
        )

    def get_config(self, guild_id: Optional[int] = None, user_id: Optional[int] = None) -> TTSConfig:
        """Get resolved TTS configuration for a guild/user scope.
        
        Returns cached config if available, otherwise loads from storage
        or returns default.
        
        Args:
            guild_id: Guild identifier or None for the default config
             
        Returns:
            TTSConfig for the guild
        """
        if guild_id is None:
            logger.warning("[CONFIG_REPO] guild_id is None, returning default config")
            return self._get_default_config()

        if user_id is not None:
            cache_key = (guild_id, user_id)
            if cache_key in self._user_cache:
                return self._clone_config(self._user_cache[cache_key])

        # Check cache first (fast path)
        if guild_id in self._cache and user_id is None:
            return self._clone_config(self._cache[guild_id])

        logger.debug(f"[CONFIG_REPO] Cache miss for guild {guild_id}, loading from storage")
        load_sync: Any = getattr(self._storage, "load_sync", None)
        if callable(load_sync):
            if user_id is not None:
                user_config = cast(TTSConfig | None, load_sync(guild_id, user_id=user_id))
                if user_config:
                    self._user_cache[(guild_id, user_id)] = self._clone_config(user_config)
                    return self._clone_config(self._user_cache[(guild_id, user_id)])
                if guild_id in self._cache:
                    return self._clone_config(self._cache[guild_id])
            config = cast(TTSConfig | None, load_sync(guild_id))
            if config:
                self._cache[guild_id] = self._clone_config(config)
                return self._clone_config(self._cache[guild_id])

        return self._get_default_config()

    async def load_config_async(self, guild_id: Optional[int] = None, user_id: Optional[int] = None) -> TTSConfig:
        """Load configuration asynchronously through the repository contract."""
        if guild_id is None:
            return self._get_default_config()
        return await self.load_from_storage(guild_id, user_id=user_id)

    async def load_from_storage(self, guild_id: Optional[int], user_id: Optional[int] = None) -> TTSConfig:
        """Load configuration from storage asynchronously.
        
        This method fetches from persistence layer and updates cache.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            TTSConfig for the guild or default if not found
        """
        if guild_id is None:
            return self._get_default_config()

        try:
            if user_id is not None:
                user_config = await self._storage.load(guild_id, user_id=user_id)
                if user_config:
                    self._user_cache[(guild_id, user_id)] = self._clone_config(user_config)
                    logger.debug(
                        "[CONFIG_REPO] Loaded config from storage for guild %s user %s",
                        guild_id,
                        user_id,
                    )
                    return self._clone_config(self._user_cache[(guild_id, user_id)])

            config = await self._storage.load(guild_id)
            
            if config:
                self._cache[guild_id] = self._clone_config(config)
                logger.debug(f"[CONFIG_REPO] Loaded config from storage for guild {guild_id}")
                return self._clone_config(self._cache[guild_id])
            logger.debug(f"[CONFIG_REPO] No config in storage for guild {guild_id}, using default")
            return self._get_default_config()

        except Exception as e:
            logger.error(f"[CONFIG_REPO] Error loading config for guild {guild_id}: {e}")
            return self._get_default_config()

    def set_config(self, guild_id: int, config: TTSConfig, user_id: Optional[int] = None) -> None:
        """Set TTS configuration for a guild or guild/user scope (in-memory only).
        
        WARNING: This only updates cache. Use save_config_async() to persist!
        
        Args:
            guild_id: Guild identifier
            config: New configuration
        """
        if guild_id is None:
            logger.warning("[CONFIG_REPO] Cannot set config for guild_id=None")
            return

        # Store copy to prevent external modification
        target = self._clone_config(config)
        if user_id is not None:
            self._user_cache[(guild_id, user_id)] = target
            logger.debug(f"[CONFIG_REPO] Updated user cache for guild {guild_id} user {user_id}")
            return

        self._cache[guild_id] = target
        logger.debug(f"[CONFIG_REPO] Updated cache for guild {guild_id}")

    async def save_config_async(self, guild_id: int, config: TTSConfig, user_id: Optional[int] = None) -> bool:
        """Save configuration to persistent storage asynchronously.
        
        Args:
            guild_id: Guild identifier
            config: Configuration to save
            
        Returns:
            True if saved successfully
        """
        if guild_id is None:
            logger.warning("[CONFIG_REPO] Cannot save config for guild_id=None")
            return False

        try:
            # Update cache first
            self.set_config(guild_id, config, user_id=user_id)

            success = await self._storage.save(guild_id, config, user_id=user_id)

            if success:
                if user_id is not None:
                    logger.info("[CONFIG_REPO] Saved config for guild %s user %s", guild_id, user_id)
                else:
                    logger.info(f"[CONFIG_REPO] Saved config for guild {guild_id}")
            else:
                if user_id is not None:
                    logger.error("[CONFIG_REPO] Failed to persist config for guild %s user %s", guild_id, user_id)
                else:
                    logger.error(f"[CONFIG_REPO] Failed to persist config for guild {guild_id}")

            return success

        except Exception as e:
            logger.error(f"[CONFIG_REPO] Error saving config for guild {guild_id}: {e}")
            return False

    async def delete_config_async(self, guild_id: int, user_id: Optional[int] = None) -> bool:
        """Delete configuration for a guild.
        
        Args:
            guild_id: Guild identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            if user_id is not None:
                self._user_cache.pop((guild_id, user_id), None)
            else:
                self._cache.pop(guild_id, None)
                user_keys = [key for key in self._user_cache if key[0] == guild_id]
                for key in user_keys:
                    self._user_cache.pop(key, None)

            # Delete from storage
            success = await self._storage.delete(guild_id, user_id=user_id)

            if success:
                if user_id is not None:
                    logger.info("[CONFIG_REPO] Deleted config for guild %s user %s", guild_id, user_id)
                else:
                    logger.info(f"[CONFIG_REPO] Deleted config for guild {guild_id}")

            return success

        except Exception as e:
            logger.error(f"[CONFIG_REPO] Error deleting config for guild {guild_id}: {e}")
            return False

    def get_effective_scope(self, guild_id: Optional[int] = None, user_id: Optional[int] = None) -> str:
        if guild_id is None:
            return "default"

        if user_id is not None:
            cache_key = (guild_id, user_id)
            if cache_key in self._user_cache:
                return "user"
            load_sync: Any = getattr(self._storage, "load_sync", None)
            if callable(load_sync) and load_sync(guild_id, user_id=user_id):
                return "user"

        if guild_id in self._cache:
            return "guild"

        load_sync = getattr(self._storage, "load_sync", None)
        if callable(load_sync) and load_sync(guild_id):
            return "guild"

        return "default"

    def _get_default_config(self) -> TTSConfig:
        """Get default configuration (defensive copy).
        
        Returns:
            Copy of default configuration
        """
        return TTSConfig(
            engine=self._default_config.engine,
            language=self._default_config.language,
            voice_id=self._default_config.voice_id,
            rate=self._default_config.rate
        )

    def clear_cache(self) -> None:
        """Clear in-memory cache (for testing or when running low on memory)."""
        size = len(self._cache)
        self._cache.clear()
        self._user_cache.clear()
        logger.info(f"[CONFIG_REPO] Cleared cache ({size} entries)")
