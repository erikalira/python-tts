"""Tests for core entities."""
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
    
    def test_equality(self):
        """Test TTSRequest equality comparison."""
        request1 = TTSRequest(text="Hello", channel_id=123)
        request2 = TTSRequest(text="Hello", channel_id=123)
        request3 = TTSRequest(text="World", channel_id=123)
        
        assert request1 == request2
        assert request1 != request3
    
    def test_repr(self):
        """Test TTSRequest string representation."""
        request = TTSRequest(text="Hello", channel_id=123)
        repr_str = repr(request)
        
        assert "TTSRequest" in repr_str
        assert "Hello" in repr_str
        assert "123" in repr_str


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
    
    def test_equality(self):
        """Test TTSConfig equality comparison."""
        config1 = TTSConfig(engine='gtts', language='pt')
        config2 = TTSConfig(engine='gtts', language='pt')
        config3 = TTSConfig(engine='pyttsx3', language='pt')
        
        assert config1 == config2
        assert config1 != config3
    
    def test_repr(self):
        """Test TTSConfig string representation."""
        config = TTSConfig(engine='gtts', language='pt')
        repr_str = repr(config)
        
        assert "TTSConfig" in repr_str
        assert "gtts" in repr_str


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
    
    def test_equality(self):
        """Test AudioFile equality comparison."""
        audio1 = AudioFile(path='/tmp/test.mp3')
        audio2 = AudioFile(path='/tmp/test.mp3')
        audio3 = AudioFile(path='/tmp/other.mp3')
        
        assert audio1 == audio2
        assert audio1 != audio3
    
    def test_repr(self):
        """Test AudioFile string representation."""
        audio = AudioFile(path='/tmp/test.mp3')
        repr_str = repr(audio)
        
        assert "AudioFile" in repr_str
        assert "/tmp/test.mp3" in repr_str
