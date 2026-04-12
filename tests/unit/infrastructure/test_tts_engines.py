"""Tests for TTS engines."""
import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from src.infrastructure.tts.engines import RoutedTTSEngine, TTSEngineFactory
from src.infrastructure.tts.audio_cleanup import FileAudioCleanup
from src.core.entities import AudioFile, TTSConfig


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

    def test_create_edge_tts_engine(self):
        """Test creating edge-tts engine."""
        config = TTSConfig(engine='edge-tts')
        engine = TTSEngineFactory.create(config)

        assert engine is not None
        from src.infrastructure.tts.engines import EdgeTTSEngine
        assert isinstance(engine, EdgeTTSEngine)
    
    def test_create_invalid_engine(self):
        """Test creating invalid engine raises error."""
        config = TTSConfig(engine='invalid')
        
        with pytest.raises(ValueError, match="Unknown TTS engine"):
            TTSEngineFactory.create(config)


@pytest.mark.asyncio
class TestRoutedTTSEngine:
    async def test_routes_to_engine_requested_by_current_config(self):
        gtts_engine = AsyncMock()
        gtts_engine.generate_audio = AsyncMock(return_value=AudioFile(path="/tmp/gtts.wav"))
        pyttsx3_engine = AsyncMock()
        pyttsx3_engine.generate_audio = AsyncMock(return_value=AudioFile(path="/tmp/pyttsx3.wav"))
        edge_engine = AsyncMock()
        edge_engine.generate_audio = AsyncMock(return_value=AudioFile(path="/tmp/edge.mp3"))

        create_calls = []

        def fake_create(config: TTSConfig):
            create_calls.append(config.engine)
            if config.engine == "gtts":
                return gtts_engine
            if config.engine == "pyttsx3":
                return pyttsx3_engine
            if config.engine == "edge-tts":
                return edge_engine
            raise AssertionError(f"unexpected engine {config.engine}")

        router = RoutedTTSEngine()
        with patch("src.infrastructure.tts.engines.TTSEngineFactory.create", side_effect=fake_create):
            first = await router.generate_audio("hello", TTSConfig(engine="gtts", language="pt"))
            second = await router.generate_audio("robot", TTSConfig(engine="pyttsx3", language="en"))
            third = await router.generate_audio("neural", TTSConfig(engine="edge-tts", language="pt-BR", voice_id="pt-BR-FranciscaNeural"))

        assert first.path == "/tmp/gtts.wav"
        assert second.path == "/tmp/pyttsx3.wav"
        assert third.path == "/tmp/edge.mp3"
        assert create_calls == ["gtts", "pyttsx3", "edge-tts"]
        gtts_engine.generate_audio.assert_awaited_once()
        pyttsx3_engine.generate_audio.assert_awaited_once()
        edge_engine.generate_audio.assert_awaited_once()


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
        cleanup = FileAudioCleanup()
        
        assert audio is not None
        assert audio.path.endswith('.wav')
        
        # Cleanup
        await cleanup.cleanup(audio)


@pytest.mark.asyncio
class TestEdgeTTSEngine:
    async def test_generate_audio_uses_selected_edge_voice(self):
        from src.infrastructure.tts.engines import EdgeTTSEngine

        saved_calls = []

        class FakeCommunicate:
            def __init__(self, text: str, voice: str, rate: str):
                saved_calls.append({"text": text, "voice": voice, "rate": rate})

            async def save(self, path: str):
                saved_calls[-1]["path"] = path

        fake_module = SimpleNamespace(Communicate=FakeCommunicate)

        with patch.dict(sys.modules, {"edge_tts": fake_module}):
            engine = EdgeTTSEngine()
            config = TTSConfig(engine="edge-tts", language="pt-BR", voice_id="pt-BR-FranciscaNeural", rate=180)
            audio = await engine.generate_audio("Oi", config)

        assert audio.path.endswith(".mp3")
        assert saved_calls[0]["voice"] == "pt-BR-FranciscaNeural"
        assert saved_calls[0]["rate"] == "+0%"
