"""Tests for configuration repository."""
from src.infrastructure.tts.config_repository import InMemoryConfigRepository
from src.core.entities import TTSConfig


class TestInMemoryConfigRepository:
    """Test InMemoryConfigRepository."""
    
    def test_get_default_config(self):
        """Test getting default configuration."""
        default_config = TTSConfig(engine='gtts', language='pt')
        repo = InMemoryConfigRepository(default_config)
        
        config = repo.get_config()
        
        assert config.engine == 'gtts'
        assert config.language == 'pt'
    
    def test_get_config_for_unknown_user(self):
        """Test getting config for guild without custom settings."""
        default_config = TTSConfig(engine='gtts', language='pt')
        repo = InMemoryConfigRepository(default_config)
        
        config = repo.get_config(guild_id=999)
        
        # Should return default
        assert config.engine == 'gtts'
        assert config.language == 'pt'
    
    def test_set_and_get_user_config(self):
        """Test setting and getting guild-specific config."""
        default_config = TTSConfig(engine='gtts', language='pt')
        repo = InMemoryConfigRepository(default_config)
        
        # Set custom config for guild
        custom_config = TTSConfig(engine='pyttsx3', language='en')
        repo.set_config(guild_id=123, config=custom_config)
        
        # Retrieve it
        config = repo.get_config(guild_id=123)
        
        assert config.engine == 'pyttsx3'
        assert config.language == 'en'
    
    def test_multiple_user_configs(self):
        """Test managing configs for multiple guilds."""
        default_config = TTSConfig(engine='gtts', language='pt')
        repo = InMemoryConfigRepository(default_config)
        
        # Set config for guild 1
        config1 = TTSConfig(engine='gtts', language='en')
        repo.set_config(guild_id=1, config=config1)
        
        # Set config for guild 2
        config2 = TTSConfig(engine='pyttsx3', language='es')
        repo.set_config(guild_id=2, config=config2)
        
        # Verify each guild has correct config
        assert repo.get_config(guild_id=1).language == 'en'
        assert repo.get_config(guild_id=2).language == 'es'
        assert repo.get_config(guild_id=3).language == 'pt'  # Default
    
    def test_config_isolation(self):
        """Test that configs are isolated (no shared references)."""
        default_config = TTSConfig(engine='gtts', language='pt')
        repo = InMemoryConfigRepository(default_config)
        
        config1 = repo.get_config()
        config2 = repo.get_config()
        
        # Modifying one shouldn't affect the other
        config1.language = 'modified'
        
        assert config2.language == 'pt'
