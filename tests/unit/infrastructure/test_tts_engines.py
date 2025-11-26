"""Tests for TTS engines."""
import pytest
from src.infrastructure.tts.engines import TTSEngineFactory
from src.core.entities import TTSConfig


class TestTTSEngineFactory:
    """Test TTSEngineFactory."""
    
    def test_create_gtts_engine(self):
        """Test creating gTTS engine."""
        config = TTSConfig(engine='gtts')
        engine = TTSEngineFactory.create(config)
        
        assert engine is not None
        from src.infrastructure.tts.engines import GTTSEngine
        assert isinstance(engine, GTTSEngine)
    
    def test_create_pyttsx3_engine(self):
        """Test creating pyttsx3 engine."""
        config = TTSConfig(engine='pyttsx3')
        engine = TTSEngineFactory.create(config)
        
        assert engine is not None
        from src.infrastructure.tts.engines import Pyttsx3Engine
        assert isinstance(engine, Pyttsx3Engine)
    
    def test_create_invalid_engine(self):
        """Test creating invalid engine raises error."""
        config = TTSConfig(engine='invalid')
        
        with pytest.raises(ValueError, match="Unknown TTS engine"):
            TTSEngineFactory.create(config)


@pytest.mark.asyncio
class TestGTTSEngine:
    """Test GTTSEngine (requires network)."""
    
    @pytest.mark.skip(reason="Requires network connection")
    async def test_generate_audio(self, sample_tts_config):
        """Test generating audio with gTTS."""
        from src.infrastructure.tts.engines import GTTSEngine
        
        engine = GTTSEngine()
        config = TTSConfig(engine='gtts', language='en')
        
        audio = await engine.generate_audio("Hello world", config)
        
        assert audio is not None
        assert audio.path.endswith('.wav')
        
        # Cleanup
        audio.cleanup()
