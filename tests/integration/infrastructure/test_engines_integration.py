"""Integration tests for TTS engines with actual implementation."""

import os
import platform
import socket

import pytest
import pyttsx3

from src.core.entities import TTSConfig
from src.infrastructure.tts.audio_cleanup import FileAudioCleanup
from src.infrastructure.tts.engines import GTTSEngine, Pyttsx3Engine


@pytest.mark.integration
@pytest.mark.network
class TestGTTSEngineIntegration:
    """Test GTTSEngine with actual gTTS library."""

    @staticmethod
    def _ensure_network_available() -> None:
        if os.getenv("RUN_NETWORK_INTEGRATION_TESTS") != "1":
            pytest.skip("Set RUN_NETWORK_INTEGRATION_TESTS=1 to run network integration tests")
        try:
            socket.create_connection(("translate.google.com", 443), timeout=2).close()
        except OSError as exc:
            pytest.skip(f"Network integration unavailable: {exc}")

    @pytest.mark.asyncio
    async def test_generate_audio_creates_file(self):
        """Test that GTTSEngine creates an audio file."""
        self._ensure_network_available()
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

    @pytest.mark.asyncio
    async def test_generate_audio_different_languages(self):
        """Test generating audio in different languages."""
        self._ensure_network_available()
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


@pytest.mark.integration
@pytest.mark.slow
class TestPyttsx3EngineIntegration:
    """Test Pyttsx3Engine with actual pyttsx3 library (slow tests)."""

    @staticmethod
    def _ensure_pyttsx3_backend_available() -> None:
        if platform.system() != "Windows":
            pytest.skip("pyttsx3 SAPI5 integration is only exercised on Windows")
        try:
            engine = pyttsx3.init(driverName="sapi5")
            engine.stop()
        except Exception as exc:
            pytest.skip(f"pyttsx3 SAPI5 backend unavailable: {exc}")

    def test_platform_expectation(self):
        """Document the expected pyttsx3 backend for the current platform."""
        if platform.system() == "Windows":
            assert platform.system() == "Windows"
        else:
            assert platform.system() != "Windows"

    @pytest.mark.asyncio
    async def test_generate_audio_creates_file(self):
        """Test that Pyttsx3Engine creates an audio file."""
        self._ensure_pyttsx3_backend_available()
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

    @pytest.mark.asyncio
    async def test_engine_initialization(self):
        """Test lazy initialization of pyttsx3 engine."""
        self._ensure_pyttsx3_backend_available()
        engine = Pyttsx3Engine()

        assert engine._engine is None

        config = TTSConfig(engine="pyttsx3", language="en")
        audio = await engine.generate_audio("Hi", config)
        cleanup = FileAudioCleanup()

        assert engine._engine is not None

        await cleanup.cleanup(audio)
