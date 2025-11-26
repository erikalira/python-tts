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
        mock_config_repository
    ):
        """Test handling valid speak request."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository
        )
        controller = SpeakController(use_case)
        
        # Create mock request using Mock
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={
            'text': 'Hello world',
            'channel_id': 123
        })
        
        response = await controller.handle(request)
        
        assert response.status == 200
    
    async def test_handle_missing_text(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository
    ):
        """Test handling request without text."""
        use_case = SpeakTextUseCase(
            tts_engine=mock_tts_engine,
            channel_repository=mock_channel_repository,
            config_repository=mock_config_repository
        )
        controller = SpeakController(use_case)
        
        # Create mock request with empty text
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={'text': ''})
        
        response = await controller.handle(request)
        
        assert response.status == 400
