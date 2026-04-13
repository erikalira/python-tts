"""Tests for application use cases."""
import asyncio

import pytest
from src.application.dto import (
    ConfigureTTSResult,
    JOIN_RESULT_OK,
    JOIN_RESULT_USER_NOT_IN_CHANNEL,
    LEAVE_RESULT_NOT_CONNECTED,
    LEAVE_RESULT_OK,
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_OK,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
    SpeakTextInputDTO,
    SpeakTextResult,
    TTSConfigurationData,
)
from src.application.use_cases import (
    ConfigureTTSUseCase,
    JoinVoiceChannelUseCase,
    LeaveVoiceChannelUseCase,
    SpeakTextUseCase,
)
from src.core.entities import TTSConfig
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
        build_speak_use_case,
        sample_tts_request
    ):
        """Test successful execution of speak use case."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        
        result = await use_case.execute(sample_tts_request)
        
        assert result.success is True
        assert result.code == SPEAK_RESULT_OK
        assert result.queued is False
        assert len(mock_tts_engine.calls) == 1
        assert len(mock_channel_repository.channel.played_audio) == 1
    
    async def test_execute_missing_text(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test execution with missing text."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        
        request = SpeakTextInputDTO(text="")
        result = await use_case.execute(request)
        
        assert result.success is False
        assert result.code == SPEAK_RESULT_MISSING_TEXT
    
    async def test_execute_no_channel_found(
        self,
        mock_tts_engine,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
        sample_tts_request
    ):
        """Test execution when no voice channel is found."""
        from tests.conftest import MockVoiceChannelRepository
        
        # Repository that returns None
        repo = MockVoiceChannelRepository(return_none=True)
        
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=repo,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        
        result = await use_case.execute(sample_tts_request)
        
        assert result.success is False
        assert result.code == SPEAK_RESULT_USER_NOT_IN_CHANNEL
        assert result.queued is False

    async def test_execute_truncates_text_with_shared_policy(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Speak use case should reuse the shared TTS text preparation rules."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
            max_text_length=5,
        )

        request = SpeakTextInputDTO(text="  abcdefgh  ", channel_id=123456, guild_id=789012, member_id=345678)
        result = await use_case.execute(request)

        assert result.success is True
        assert mock_tts_engine.calls[0]["text"] == "abcde"

    async def test_execute_infers_guild_id_from_member_channel_when_missing(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Speak use case should derive the guild from the member's current voice channel."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )

        request = SpeakTextInputDTO(text="test", member_id=345678)
        result = await use_case.execute(request)

        assert result.success is True
        assert mock_tts_engine.calls[0]["config"].language == "pt"
        assert mock_channel_repository.channel.played_audio
    
    async def test_execute_finds_by_channel_id(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test that use case finds channel by channel_id first."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        
        request = SpeakTextInputDTO(text="test", channel_id=123456, guild_id=789012, member_id=345678)
        result = await use_case.execute(request)
        
        assert result.success is True
        assert mock_channel_repository.channel.is_connected()

    async def test_execute_keeps_processing_flag_while_background_queue_is_draining(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        build_speak_use_case,
        sample_tts_request
    ):
        """A new request must stay queued while a background item is still playing."""
        audio_queue = InMemoryAudioQueue()
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=audio_queue,
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

            return SpeakTextResult(
                success=True,
                code=SPEAK_RESULT_OK,
                queued=False,
                item_id=item.item_id,
            )

        use_case._queue_orchestrator._process_item = fake_process_audio

        first_request = SpeakTextInputDTO(text="first", channel_id=123456, guild_id=789012, member_id=345678)
        second_request = SpeakTextInputDTO(text="second", channel_id=123456, guild_id=789012, member_id=345678)
        third_request = SpeakTextInputDTO(text="third", channel_id=123456, guild_id=789012, member_id=345678)

        first_task = asyncio.create_task(use_case.execute(first_request))
        await asyncio.wait_for(first_started.wait(), timeout=1)

        second_result = await use_case.execute(second_request)
        assert second_result.queued is True
        assert second_result.code == SPEAK_RESULT_QUEUED
        assert second_result.position == 0

        first_release.set()
        first_result = await asyncio.wait_for(first_task, timeout=1)
        assert first_result.success is True

        await asyncio.wait_for(second_started.wait(), timeout=1)

        third_result = await use_case.execute(third_request)
        assert third_result.success is True
        assert third_result.queued is True
        assert third_result.code == SPEAK_RESULT_QUEUED
        assert third_result.position == 0
        assert process_order == ["first", "second"]

        second_release.set()
        await asyncio.sleep(0.6)

        assert process_order == ["first", "second", "third"]

    async def test_execute_returns_failure_when_queue_is_full(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        build_speak_use_case,
        sample_tts_request
    ):
        """Queue overflow should reject the request instead of faking a queued success."""
        audio_queue = InMemoryAudioQueue(max_queue_size=0)
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=audio_queue,
        )

        result = await use_case.execute(sample_tts_request)

        assert result.success is False
        assert result.code == SPEAK_RESULT_QUEUE_FULL
        assert result.queued is False


class TestConfigureTTSUseCase:
    """Test ConfigureTTSUseCase."""
    
    @pytest.mark.asyncio
    async def test_get_current_config(self, mock_config_repository):
        """Test getting current configuration."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = use_case.get_config(guild_id=123)
        
        assert result == ConfigureTTSResult(
            success=True,
            guild_id=123,
            config=TTSConfigurationData(
                engine="gtts",
                language="pt",
                voice_id="roa/pt-br",
                rate=180,
            ),
            scope="default",
        )
        assert result.config is not None
        assert result.config.engine == "gtts"
        assert result.config.language == "pt"
    
    @pytest.mark.asyncio
    async def test_update_engine(self, mock_config_repository):
        """Test updating TTS engine."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = await use_case.update_config_async(guild_id=123, engine="pyttsx3")
        
        assert result.success is True
        assert result.config is not None
        assert result.config.engine == "pyttsx3"
        
        # Verify it was saved
        saved_config = mock_config_repository.get_config(123)
        assert saved_config.engine == "pyttsx3"
    
    @pytest.mark.asyncio
    async def test_update_language(self, mock_config_repository):
        """Test updating TTS language."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = await use_case.update_config_async(guild_id=123, language="en")
        
        assert result.success is True
        assert result.config is not None
        assert result.config.language == "en"
    
    @pytest.mark.asyncio
    async def test_update_voice_id(self, mock_config_repository):
        """Test updating voice ID."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = await use_case.update_config_async(guild_id=123, voice_id="en-us")
        
        assert result.success is True
        assert result.config is not None
        assert result.config.voice_id == "en-us"

    @pytest.mark.asyncio
    async def test_update_user_scoped_voice_id(self, mock_config_repository):
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)

        result = await use_case.update_config_async(guild_id=123, user_id=999, voice_id="Maria")

        assert result.success is True
        assert mock_config_repository.get_config(123, user_id=999).voice_id == "Maria"

    @pytest.mark.asyncio
    async def test_reset_user_scoped_voice_id(self, mock_config_repository):
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        await use_case.update_config_async(guild_id=123, user_id=999, voice_id="Maria")
        await use_case.update_config_async(guild_id=123, voice_id="David")

        result = await use_case.reset_config_async(guild_id=123, user_id=999)

        assert result.success is True
        assert result.scope == "guild"
        assert result.config is not None
        assert result.config.voice_id == "David"

    @pytest.mark.asyncio
    async def test_update_edge_tts_engine(self, mock_config_repository):
        """Test updating TTS engine to edge-tts."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)

        result = await use_case.update_config_async(guild_id=123, engine="edge-tts")

        assert result.success is True
        assert result.config is not None
        assert result.config.engine == "edge-tts"
    
    @pytest.mark.asyncio
    async def test_invalid_engine(self, mock_config_repository):
        """Test setting invalid engine."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = await use_case.update_config_async(guild_id=123, engine="invalid")
        
        assert result == ConfigureTTSResult(
            success=False,
            message="Invalid engine. Use 'gtts', 'pyttsx3' or 'edge-tts'",
        )
        assert result.message is not None
        assert "Invalid engine" in result.message


@pytest.mark.asyncio
class TestVoiceChannelUseCases:
    """Test voice channel connection use cases."""

    async def test_join_voice_channel_success(self, mock_channel_repository):
        """Join use case should connect to the member channel."""
        use_case = JoinVoiceChannelUseCase(mock_channel_repository)

        result = await use_case.execute(guild_id=789012, member_id=345678)

        assert result.success is True
        assert result.code == JOIN_RESULT_OK
        assert mock_channel_repository.channel.is_connected() is True

    async def test_join_voice_channel_requires_member_channel(self):
        """Join use case should fail when the member is not in voice."""
        from tests.conftest import MockVoiceChannelRepository

        use_case = JoinVoiceChannelUseCase(MockVoiceChannelRepository(return_none=True))

        result = await use_case.execute(guild_id=789012, member_id=345678)

        assert result.success is False
        assert result.code == JOIN_RESULT_USER_NOT_IN_CHANNEL

    async def test_leave_voice_channel_success(self, mock_channel_repository):
        """Leave use case should disconnect an active guild voice channel."""
        use_case = LeaveVoiceChannelUseCase(mock_channel_repository)
        await mock_channel_repository.channel.connect()

        result = await use_case.execute(guild_id=789012)

        assert result.success is True
        assert result.code == LEAVE_RESULT_OK
        assert mock_channel_repository.channel.is_connected() is False

    async def test_leave_voice_channel_when_not_connected(self, mock_channel_repository):
        """Leave use case should report not connected when no voice session exists."""
        use_case = LeaveVoiceChannelUseCase(mock_channel_repository)

        result = await use_case.execute(guild_id=789012)

        assert result.success is False
        assert result.code == LEAVE_RESULT_NOT_CONNECTED
    
    @pytest.mark.asyncio
    async def test_update_multiple_settings(self, mock_config_repository):
        """Test updating multiple settings at once."""
        use_case = ConfigureTTSUseCase(config_repository=mock_config_repository)
        
        result = await use_case.update_config_async(
            guild_id=123,
            engine="pyttsx3",
            language="en",
            voice_id="en-us"
        )
        
        assert result.success is True
        assert result.config is not None
        assert result.config.engine == "pyttsx3"
        assert result.config.language == "en"
        assert result.config.voice_id == "en-us"
