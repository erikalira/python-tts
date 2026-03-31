"""Tests for application use cases."""
import pytest
from src.application.use_cases import SpeakTextUseCase, ConfigureTTSUseCase
from src.core.entities import TTSRequest, TTSConfig


@pytest.mark.asyncio
class TestSpeakTextUseCase:
    """Test SpeakTextUseCase."""
    
    async def test_execute_success(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        sample_tts_request
    ):
        """Test successful execution of speak use case."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository
        )
        
        result = await use_case.execute(sample_tts_request)
        
        assert result["success"] is True
        assert "Áudio reproduzido" in result["message"]  # Check for emoji and message
        assert "channel_changed" in result
        assert len(mock_tts_engine.calls) == 1
        assert len(mock_channel_repository.channel.played_audio) == 1
    
    async def test_execute_missing_text(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test execution with missing text."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository
        )
        
        request = TTSRequest(text="")
        result = await use_case.execute(request)
        
        assert result["success"] is False
        assert result["message"] == "missing text"
    
    async def test_execute_no_channel_found(
        self,
        mock_tts_engine,
        mock_config_repository,
        sample_tts_request
    ):
        """Test execution when no voice channel is found."""
        from tests.conftest import MockVoiceChannelRepository
        
        # Repository that returns None
        repo = MockVoiceChannelRepository(return_none=True)
        
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=repo,
            config_repository=mock_config_repository
        )
        
        result = await use_case.execute(sample_tts_request)
        
        assert result["success"] is False
        assert "não está em nenhuma sala" in result["message"]  # Check for new error message
        assert result["channel_changed"] is False
    
    async def test_execute_finds_by_channel_id(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test that use case finds channel by channel_id first."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository
        )
        
        request = TTSRequest(text="test", channel_id=123, member_id=1231231)
        result = await use_case.execute(request)
        
        assert result["success"] is True
        assert mock_channel_repository.channel.is_connected()


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
