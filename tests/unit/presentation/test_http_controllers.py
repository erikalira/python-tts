"""Tests for HTTP controllers."""
import pytest
from unittest.mock import Mock, AsyncMock
from aiohttp import web
from src.presentation.http_controllers import SpeakController
from src.application.use_cases import SpeakTextUseCase


@pytest.mark.asyncio
class TestSpeakController:
    """Test SpeakController."""
    
    async def test_handle_valid_request(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Test handling valid speak request."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        controller = SpeakController(use_case)
        
        # Create mock request using Mock
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={
            'text': 'Hello world',
            'guild_id': 789012,
            'channel_id': 123456,
            'member_id': 345678
        })
        
        response = await controller.handle(request)
        
        assert response.status == 200
    
    async def test_handle_missing_text(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Test handling request without text."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        controller = SpeakController(use_case)
        
        # Create mock request with empty text
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={'text': ''})
        
        response = await controller.handle(request)
        
        assert response.status == 400
    
    async def test_handle_invalid_json(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Test handling request with invalid JSON."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        controller = SpeakController(use_case)
        
        # Create mock request that raises exception on json()
        request = Mock(spec=web.Request)
        request.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        
        response = await controller.handle(request)
        
        assert response.status == 400
        assert "invalid json" in response.text.lower()
    
    async def test_handle_with_all_fields(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Test handling request with all fields."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        controller = SpeakController(use_case)
        
        # Create mock request with all fields
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={
            'text': 'Hello world',
            'channel_id': 123456,
            'guild_id': 789012,
            'member_id': 345678
        })
        
        response = await controller.handle(request)
        
        assert response.status == 200
    
    async def test_handle_with_user_id(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Test handling request with user_id instead of member_id."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        controller = SpeakController(use_case)
        
        # Create mock request with user_id
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={
            'text': 'Hello',
            'guild_id': 789012,
            'user_id': 345678
        })
        
        response = await controller.handle(request)
        
        assert response.status == 200
    
    async def test_parse_int_with_invalid_values(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue
    ):
        """Test _parse_int with various invalid values."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository,
            audio_queue=mock_audio_queue
        )
        controller = SpeakController(use_case)
        
        # Test None
        assert controller._parse_int(None) is None
        
        # Test invalid string
        assert controller._parse_int("invalid") is None
        
        # Test valid string
        assert controller._parse_int("123") == 123
        
        # Test integer
        assert controller._parse_int(456) == 456
        
        # Test float
        assert controller._parse_int(789.5) == 789
