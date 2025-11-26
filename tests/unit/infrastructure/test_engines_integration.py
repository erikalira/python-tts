"""Integration tests for TTS engines with actual implementation."""
import pytest
import os
from src.infrastructure.tts.engines import GTTSEngine, Pyttsx3Engine
from src.core.entities import TTSConfig


@pytest.mark.asyncio
class TestGTTSEngineIntegration:
    """Test GTTSEngine with actual gTTS library."""
    
    async def test_generate_audio_creates_file(self):
        """Test that GTTSEngine creates an audio file."""
        engine = GTTSEngine()
        config = TTSConfig(engine='gtts', language='en')
        
        audio = await engine.generate_audio("Hello", config)
        
        # Check file was created
        assert audio is not None
        assert audio.path is not None
        assert os.path.exists(audio.path)
        assert audio.path.endswith('.wav')
        
        # Cleanup
        audio.cleanup()
        assert not os.path.exists(audio.path)
    
    async def test_generate_audio_different_languages(self):
        """Test generating audio in different languages."""
        engine = GTTSEngine()
        
        # English
        config_en = TTSConfig(engine='gtts', language='en')
        audio_en = await engine.generate_audio("Hi", config_en)
        assert os.path.exists(audio_en.path)
        audio_en.cleanup()
        
        # Portuguese
        config_pt = TTSConfig(engine='gtts', language='pt')
        audio_pt = await engine.generate_audio("Oi", config_pt)
        assert os.path.exists(audio_pt.path)
        audio_pt.cleanup()


@pytest.mark.asyncio
@pytest.mark.slow
class TestPyttsx3EngineIntegration:
    """Test Pyttsx3Engine with actual pyttsx3 library (slow tests)."""
    
    async def test_generate_audio_creates_file(self):
        """Test that Pyttsx3Engine creates an audio file."""
        engine = Pyttsx3Engine()
        config = TTSConfig(engine='pyttsx3', language='en', rate=150)
        
        audio = await engine.generate_audio("Test", config)
        
        # Check file was created
        assert audio is not None
        assert audio.path is not None
        assert os.path.exists(audio.path)
        assert audio.path.endswith('.wav')
        
        # Cleanup
        audio.cleanup()
        assert not os.path.exists(audio.path)
    
    async def test_engine_initialization(self):
        """Test lazy initialization of pyttsx3 engine."""
        engine = Pyttsx3Engine()
        
        # Engine should not be initialized yet
        assert engine._engine is None
        
        # Generate audio triggers initialization
        config = TTSConfig(engine='pyttsx3', language='en')
        audio = await engine.generate_audio("Hi", config)
        
        # Now engine should be initialized
        assert engine._engine is not None
        
        audio.cleanup()
