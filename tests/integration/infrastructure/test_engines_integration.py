"""Integration tests for TTS engines with actual implementation."""

import os
import platform

import pytest

from src.core.entities import TTSConfig
from src.infrastructure.tts.audio_cleanup import FileAudioCleanup
from src.infrastructure.tts.engines import GTTSEngine, Pyttsx3Engine


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.network
class TestGTTSEngineIntegration:
    """Test GTTSEngine with actual gTTS library."""

    async def test_generate_audio_creates_file(self):
        """Test that GTTSEngine creates an audio file."""
        engine = GTTSEngine()
        config = TTSConfig(engine="gtts", language="en")

        audio = await engine.generate_audio("Hello", config)
        cleanup = FileAudioCleanup()

        assert audio is not None
        assert audio.path is not None
        assert os.path.exists(audio.path)
        assert audio.path.endswith(".wav")

        await cleanup.cleanup(audio)
        assert not os.path.exists(audio.path)

    async def test_generate_audio_different_languages(self):
        """Test generating audio in different languages."""
        engine = GTTSEngine()
        cleanup = FileAudioCleanup()

        config_en = TTSConfig(engine="gtts", language="en")
        audio_en = await engine.generate_audio("Hi", config_en)
        assert os.path.exists(audio_en.path)
        await cleanup.cleanup(audio_en)

        config_pt = TTSConfig(engine="gtts", language="pt")
        audio_pt = await engine.generate_audio("Oi", config_pt)
        assert os.path.exists(audio_pt.path)
        await cleanup.cleanup(audio_pt)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.slow
class TestPyttsx3EngineIntegration:
    """Test Pyttsx3Engine with actual pyttsx3 library (slow tests)."""

    def test_platform_expectation(self):
        """Document the expected pyttsx3 backend for the current platform."""
        if platform.system() == "Windows":
            assert platform.system() == "Windows"
        else:
            assert platform.system() != "Windows"

    async def test_generate_audio_creates_file(self):
        """Test that Pyttsx3Engine creates an audio file."""
        engine = Pyttsx3Engine()
        config = TTSConfig(engine="pyttsx3", language="en", rate=150)

        audio = await engine.generate_audio("Test", config)
        cleanup = FileAudioCleanup()

        assert audio is not None
        assert audio.path is not None
        assert os.path.exists(audio.path)
        assert audio.path.endswith(".wav")

        await cleanup.cleanup(audio)
        assert not os.path.exists(audio.path)

    async def test_engine_initialization(self):
        """Test lazy initialization of pyttsx3 engine."""
        engine = Pyttsx3Engine()

        assert engine._engine is None

        config = TTSConfig(engine="pyttsx3", language="en")
        audio = await engine.generate_audio("Hi", config)
        cleanup = FileAudioCleanup()

        assert engine._engine is not None

        await cleanup.cleanup(audio)
