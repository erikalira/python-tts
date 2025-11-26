"""HTTP controllers for handling web requests."""
import logging
from aiohttp import web
from src.application.use_cases import SpeakTextUseCase
from src.core.entities import TTSRequest

logger = logging.getLogger(__name__)


class SpeakController:
    """Controller for /speak endpoint.
    
    Follows Single Responsibility: only handles HTTP request/response.
    Business logic delegated to use case.
    """
    
    def __init__(self, speak_use_case: SpeakTextUseCase):
        """Initialize controller with use case.
        
        Args:
            speak_use_case: Use case for speaking text
        """
        self._speak_use_case = speak_use_case
    
    async def handle(self, request: web.Request) -> web.Response:
        """Handle POST /speak request.
        
        Args:
            request: aiohttp request
            
        Returns:
            aiohttp response
        """
        try:
            data = await request.json()
        except Exception as e:
            logger.error(f"Invalid JSON: {e}")
            return web.Response(text='invalid json', status=400)
        
        # Create TTS request from HTTP data
        tts_request = TTSRequest(
            text=data.get('text', ''),
            channel_id=self._parse_int(data.get('channel_id')),
            guild_id=self._parse_int(data.get('guild_id')),
            member_id=self._parse_int(data.get('member_id') or data.get('user_id'))
        )
        
        # Execute use case
        result = await self._speak_use_case.execute(tts_request)
        
        if result["success"]:
            return web.Response(text=result["message"])
        else:
            return web.Response(text=result["message"], status=400)
    
    def _parse_int(self, value) -> int | None:
        """Safely parse integer from value."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None
