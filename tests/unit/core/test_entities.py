"""Tests for core entities."""
import pytest
from src.core.entities import TTSRequest, TTSConfig, AudioFile


class TestTTSRequest:
    """Test TTSRequest entity."""
    
    def test_create_with_all_fields(self):
        """Test creating TTSRequest with all fields."""
        request = TTSRequest(
            text="Hello",
            channel_id=123,
            guild_id=456,
            member_id=789
        )
        
        assert request.text == "Hello"
        assert request.channel_id == 123
        assert request.guild_id == 456
        assert request.member_id == 789
    
    def test_create_with_only_text(self):
        """Test creating TTSRequest with only text."""
        request = TTSRequest(text="Hello")
        
        assert request.text == "Hello"
        assert request.channel_id is None
        assert request.guild_id is None
        assert request.member_id is None


class TestTTSConfig:
    """Test TTSConfig entity."""
    
    def test_default_config(self):
        """Test default TTSConfig values."""
        config = TTSConfig()
        
        assert config.engine == 'gtts'
        assert config.language == 'pt'
        assert config.voice_id == 'roa/pt-br'
        assert config.rate == 180
    
    def test_custom_config(self):
        """Test custom TTSConfig values."""
        config = TTSConfig(
            engine='pyttsx3',
            language='en',
            voice_id='en-us',
            rate=200
        )
        
        assert config.engine == 'pyttsx3'
        assert config.language == 'en'
        assert config.voice_id == 'en-us'
        assert config.rate == 200


class TestAudioFile:
    """Test AudioFile entity."""
    
    def test_create_audio_file(self):
        """Test creating AudioFile."""
        audio = AudioFile(path="/tmp/test.wav")
        
        assert audio.path == "/tmp/test.wav"
    
    def test_cleanup_nonexistent_file(self):
        """Test cleanup of nonexistent file doesn't raise error."""
        audio = AudioFile(path="/nonexistent/file.wav")
        
        # Should not raise exception
        audio.cleanup()
