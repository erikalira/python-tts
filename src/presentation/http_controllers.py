"""HTTP controllers for handling web requests."""
import logging
from aiohttp import web
from src.application.use_cases import (
    GetCurrentVoiceContextUseCase,
    SpeakTextUseCase,
    SPEAK_RESULT_CROSS_GUILD_CHANNEL,
    VOICE_CONTEXT_RESULT_MEMBER_REQUIRED,
    VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL,
    SPEAK_RESULT_MISSING_GUILD_ID,
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_OK,
    SPEAK_RESULT_PLAYBACK_TIMEOUT,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_UNKNOWN_ERROR,
    SPEAK_RESULT_USER_LEFT_CHANNEL,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
    SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
    SPEAK_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_VOICE_PERMISSION_DENIED,
)
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
        return web.Response(
            text=self._build_message(result),
            status=self._get_status_code(result)
        )
    
    def _parse_int(self, value) -> int | None:
        """Safely parse integer from value."""
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _build_message(self, result: dict) -> str:
        """Map a neutral application result to an HTTP response message."""
        code = result.get("code")
        if code == SPEAK_RESULT_OK:
            return "audio played"
        if code == SPEAK_RESULT_QUEUED:
            position = result.get("position", 0) + 1
            queue_size = result.get("queue_size", position)
            return f"queued at position {position}/{queue_size}"
        if code == SPEAK_RESULT_MISSING_TEXT:
            return "missing text"
        if code == SPEAK_RESULT_USER_NOT_IN_CHANNEL:
            return "user is not connected to a voice channel"
        if code == SPEAK_RESULT_QUEUE_FULL:
            return "audio queue is full"
        if code == SPEAK_RESULT_MISSING_GUILD_ID:
            return "missing guild id"
        if code == SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND:
            return "voice channel not found"
        if code == SPEAK_RESULT_CROSS_GUILD_CHANNEL:
            return "voice channel belongs to another guild"
        if code == SPEAK_RESULT_USER_LEFT_CHANNEL:
            return "user left the voice channel"
        if code == SPEAK_RESULT_PLAYBACK_TIMEOUT:
            return "playback timeout"
        if code == SPEAK_RESULT_VOICE_CONNECTION_FAILED:
            return "failed to connect to voice channel"
        if code == SPEAK_RESULT_VOICE_PERMISSION_DENIED:
            return "missing voice permissions"
        if code == SPEAK_RESULT_UNKNOWN_ERROR:
            return "playback failed"
        return "unknown speak result"

    def _get_status_code(self, result: dict) -> int:
        """Map a neutral application result to an HTTP status code."""
        code = result.get("code")
        if code in (SPEAK_RESULT_OK, SPEAK_RESULT_QUEUED):
            return 200
        return 400


class VoiceContextController:
    """Controller for querying the current voice context for a member."""

    def __init__(self, voice_context_use_case: GetCurrentVoiceContextUseCase):
        self._voice_context_use_case = voice_context_use_case

    async def handle(self, request: web.Request) -> web.Response:
        member_id = self._parse_int(
            request.query.get("member_id") or request.query.get("user_id")
        )
        result = await self._voice_context_use_case.execute(member_id)
        return web.json_response(result, status=self._get_status_code(result))

    def _parse_int(self, value) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

    def _get_status_code(self, result: dict) -> int:
        code = result.get("code")
        if code == VOICE_CONTEXT_RESULT_MEMBER_REQUIRED:
            return 400
        if code == VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL:
            return 404
        return 200
