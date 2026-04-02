"""Tests for application use cases."""
import asyncio

import pytest
from src.application.use_cases import SpeakTextUseCase, ConfigureTTSUseCase
from src.core.entities import TTSRequest, TTSConfig
from src.infrastructure.audio_queue import InMemoryAudioQueue


@pytest.mark.asyncio
class TestSpeakTextUseCase:
    """Test SpeakTextUseCase."""
    
    async def test_execute_success(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        sample_tts_request
    ):
        """Test successful execution of speak use case."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        
        result = await use_case.execute(sample_tts_request)
        
        assert result["success"] is True
        assert "Áudio reproduzido" in result["message"]  # Check for emoji and message
        assert "queued" in result
        assert len(mock_tts_engine.calls) == 1
        assert len(mock_channel_repository.channel.played_audio) == 1
    
    async def test_execute_missing_text(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Test execution with missing text."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        
        request = TTSRequest(text="")
        result = await use_case.execute(request)
        
        assert result["success"] is False
        assert result["message"] == "missing text"
    
    async def test_execute_no_channel_found(
        self,
        mock_tts_engine,
        mock_config_repository,
        mock_audio_queue,
        sample_tts_request
    ):
        """Test execution when no voice channel is found."""
        from tests.conftest import MockVoiceChannelRepository
        
        # Repository that returns None
        repo = MockVoiceChannelRepository(return_none=True)
        
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=repo,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        
        result = await use_case.execute(sample_tts_request)
        
        assert result["success"] is False
        assert "não está em nenhuma sala" in result["message"]  # Check for new error message
        assert result["queued"] is False
    
    async def test_execute_finds_by_channel_id(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Test that use case finds channel by channel_id first."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        
        request = TTSRequest(text="test", channel_id=123456, guild_id=789012, member_id=345678)
        result = await use_case.execute(request)
        
        assert result["success"] is True
        assert mock_channel_repository.channel.is_connected()

    async def test_execute_keeps_processing_flag_while_background_queue_is_draining(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        sample_tts_request
    ):
        """A new request must stay queued while a background item is still playing."""
        audio_queue = InMemoryAudioQueue()
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=audio_queue
        )

        first_started = asyncio.Event()
        first_release = asyncio.Event()
        second_started = asyncio.Event()
        second_release = asyncio.Event()
        process_order = []

        async def fake_process_audio(item):
            process_order.append(item.request.text)
            if item.request.text == "first":
                first_started.set()
                await first_release.wait()
            elif item.request.text == "second":
                second_started.set()
                await second_release.wait()

            return {
                "success": True,
                "message": "✅ Áudio reproduzido",
                "queued": False,
                "item_id": item.item_id,
            }

        use_case._process_audio = fake_process_audio

        first_request = TTSRequest(text="first", channel_id=123456, guild_id=789012, member_id=345678)
        second_request = TTSRequest(text="second", channel_id=123456, guild_id=789012, member_id=345678)
        third_request = TTSRequest(text="third", channel_id=123456, guild_id=789012, member_id=345678)

        first_task = asyncio.create_task(use_case.execute(first_request))
        await asyncio.wait_for(first_started.wait(), timeout=1)

        second_result = await use_case.execute(second_request)
        assert second_result["queued"] is True
        assert second_result["position"] == 0

        first_release.set()
        first_result = await asyncio.wait_for(first_task, timeout=1)
        assert first_result["success"] is True

        await asyncio.wait_for(second_started.wait(), timeout=1)

        third_result = await use_case.execute(third_request)
        assert third_result["success"] is True
        assert third_result["queued"] is True
        assert third_result["position"] == 0
        assert process_order == ["first", "second"]

        second_release.set()
        await asyncio.sleep(0.6)

        assert process_order == ["first", "second", "third"]


class TestConfigureTTSUseCase:
    """Test ConfigureTTSUseCase."""
    
    def test_get_current_config(self, mock_config_repository):
        """Test getting current configuration."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = use_case.execute(user_id=123)
        
        assert result["success"] is True
        assert "config" in result
        assert result["config"]["engine"] == "gtts"
        assert result["config"]["language"] == "pt"
    
    def test_update_engine(self, mock_config_repository):
        """Test updating TTS engine."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = use_case.execute(user_id=123, engine="pyttsx3")
        
        assert result["success"] is True
        assert result["config"]["engine"] == "pyttsx3"
        
        # Verify it was saved
        saved_config = mock_config_repository.get_config(123)
        assert saved_config.engine == "pyttsx3"
    
    def test_update_language(self, mock_config_repository):
        """Test updating TTS language."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = use_case.execute(user_id=123, language="en")
        
        assert result["success"] is True
        assert result["config"]["language"] == "en"
    
    def test_update_voice_id(self, mock_config_repository):
        """Test updating voice ID."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = use_case.execute(user_id=123, voice_id="en-us")
        
        assert result["success"] is True
        assert result["config"]["voice_id"] == "en-us"
    
    def test_invalid_engine(self, mock_config_repository):
        """Test setting invalid engine."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = use_case.execute(user_id=123, engine="invalid")
        
        assert result["success"] is False
        assert "Invalid engine" in result["message"]
    
    def test_update_multiple_settings(self, mock_config_repository):
        """Test updating multiple settings at once."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = use_case.execute(
            user_id=123,
            engine="pyttsx3",
            language="en",
            voice_id="en-us"
        )
        
        assert result["success"] is True
        assert result["config"]["engine"] == "pyttsx3"
        assert result["config"]["language"] == "en"
        assert result["config"]["voice_id"] == "en-us"
