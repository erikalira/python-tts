"""Tests for HTTP controllers."""

import pytest
from unittest.mock import Mock, AsyncMock
from aiohttp import web

from src.core.entities import TTSConfig
from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime
from src.infrastructure.rate_limiting import InMemoryRateLimiter
from src.presentation.http_controllers import SpeakController, VoiceContextController
from src.application.dto import SpeakTextResult
from src.application.use_cases import GetCurrentVoiceContextUseCase, SpeakTextUseCase


@pytest.mark.asyncio
class TestSpeakController:
    """Test SpeakController."""
    
    async def test_handle_valid_request(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test handling valid speak request."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
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
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test handling request without text."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        controller = SpeakController(use_case)
        
        # Create mock request with empty text
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={'text': ''})
        
        response = await controller.handle(request)
        
        assert response.status == 400
        assert response.text == "missing text"

    async def test_handle_null_text_as_missing_text(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test handling request with null text payload."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        controller = SpeakController(use_case)

        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={"text": None})

        response = await controller.handle(request)

        assert response.status == 400
        assert response.text == "missing text"

    async def test_handle_non_string_text_as_missing_text(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test handling request with non-string text payload."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        controller = SpeakController(use_case)

        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={"text": 123})

        response = await controller.handle(request)

        assert response.status == 400
        assert response.text == "missing text"
    
    async def test_handle_invalid_json(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test handling request with invalid JSON."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        controller = SpeakController(use_case)
        
        # Create mock request that raises exception on json()
        request = Mock(spec=web.Request)
        request.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
        
        response = await controller.handle(request)
        
        assert response.status == 400
        assert "invalid json" in response.text.lower()

    async def test_handle_rejects_non_json_content_type(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0)
        )
        controller = SpeakController(use_case)
        request = Mock(spec=web.Request)
        request.headers = {}
        request.content_type = "text/plain"
        request.json = AsyncMock(return_value={"text": "Hello"})

        response = await controller.handle(request)

        assert response.status == 415
        assert response.text == "unsupported media type"
        use_case.execute.assert_not_awaited()

    async def test_handle_rejects_json_array_payload(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0)
        )
        controller = SpeakController(use_case)
        request = Mock(spec=web.Request)
        request.headers = {}
        request.json = AsyncMock(return_value=["not", "object"])

        response = await controller.handle(request)

        assert response.status == 400
        assert response.text == "invalid json object"
        use_case.execute.assert_not_awaited()

    async def test_handle_rejects_text_above_configured_limit(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0)
        )
        controller = SpeakController(use_case, max_text_length=5)
        request = Mock(spec=web.Request)
        request.headers = {}
        request.json = AsyncMock(return_value={"text": "too long"})

        response = await controller.handle(request)

        assert response.status == 413
        assert response.text == "text too long"
        use_case.execute.assert_not_awaited()
    
    async def test_handle_with_all_fields(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test handling request with all fields."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
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
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test handling request with user_id instead of member_id."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
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

    async def test_handle_rate_limits_by_guild_and_member(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0)
        )
        controller = SpeakController(
            use_case,
            rate_limiter=InMemoryRateLimiter(clock=lambda: 100.0),
            rate_limit_max_requests=1,
            rate_limit_window_seconds=10,
        )
        request = Mock(spec=web.Request)
        request.headers = {}
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012, "member_id": 345678})

        first_response = await controller.handle(request)
        second_response = await controller.handle(request)

        assert first_response.status == 200
        assert second_response.status == 429
        assert "rate limit exceeded" in second_response.text
        assert use_case.execute.await_count == 1

    async def test_handle_rejects_missing_auth_token_when_configured(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0)
        )
        controller = SpeakController(use_case, auth_token="secret")
        request = Mock(spec=web.Request)
        request.headers = {}
        request.json = AsyncMock(return_value={"text": "Hello"})

        response = await controller.handle(request)

        assert response.status == 401
        assert response.text == "unauthorized"
        use_case.execute.assert_not_awaited()

    async def test_handle_accepts_configured_auth_token(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0)
        )
        controller = SpeakController(use_case, auth_token="secret")
        request = Mock(spec=web.Request)
        request.headers = {"X-Bot-Token": "secret"}
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012, "member_id": 345678})

        response = await controller.handle(request)

        assert response.status == 200
        use_case.execute.assert_awaited_once()

    async def test_handle_accepts_bearer_auth_token(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0)
        )
        controller = SpeakController(use_case, auth_token="secret")
        request = Mock(spec=web.Request)
        request.headers = {"Authorization": "Bearer secret"}
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012, "member_id": 345678})

        response = await controller.handle(request)

        assert response.status == 200
        use_case.execute.assert_awaited_once()

    async def test_handle_injects_trace_context_when_otel_is_available(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(
            return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0)
        )
        otel_runtime = Mock(spec=OpenTelemetryRuntime)
        otel_runtime.start_http_span.return_value = _FakeSpanContext()
        otel_runtime.inject_current_context.return_value = {"traceparent": "00-abc-123-01"}
        controller = SpeakController(use_case, otel_runtime=otel_runtime)

        request = Mock(spec=web.Request)
        request.headers = {}
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012, "member_id": 345678})

        response = await controller.handle(request)

        assert response.status == 200
        execute_dto = use_case.execute.await_args.args[0]
        assert execute_dto.trace_context == {"traceparent": "00-abc-123-01"}

    async def test_parse_int_with_invalid_values(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Test _parse_int with various invalid values."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
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

    def test_parse_config_override_reads_nested_payload(self):
        controller = SpeakController(Mock(spec=SpeakTextUseCase))

        override = controller._parse_config_override(
            {
                "config_override": {
                    "engine": "edge-tts",
                    "language": "pt-BR",
                    "voice_id": "pt-BR-FranciscaNeural",
                    "rate": 210,
                }
            }
        )

        assert override is not None
        assert override.engine == "edge-tts"
        assert override.language == "pt-BR"
        assert override.voice_id == "pt-BR-FranciscaNeural"
        assert override.rate == 210

    def test_parse_config_override_merges_partial_payload_with_guild_config(self, mock_config_repository):
        mock_config_repository.set_config(
            789012,
            TTSConfig(
                engine="edge-tts",
                language="pt-BR",
                voice_id="pt-BR-FranciscaNeural",
                rate=210,
            ),
        )
        controller = SpeakController(
            Mock(spec=SpeakTextUseCase),
            config_repository=mock_config_repository,
        )

        override = controller._parse_config_override(
            {
                "config_override": {
                    "voice_id": "pt-BR-AntonioNeural",
                }
            },
            guild_id=789012,
        )

        assert override is not None
        assert override.engine == "edge-tts"
        assert override.language == "pt-BR"
        assert override.voice_id == "pt-BR-AntonioNeural"
        assert override.rate == 210


@pytest.mark.asyncio
class TestVoiceContextController:
    async def test_handle_returns_current_voice_context(self, mock_channel_repository):
        controller = VoiceContextController(
            GetCurrentVoiceContextUseCase(mock_channel_repository)
        )
        request = Mock(spec=web.Request)
        request.query = {"member_id": "345678"}

        response = await controller.handle(request)

        assert response.status == 200
        assert "Mock Guild" in response.text
        assert "Mock Voice" in response.text

    async def test_handle_accepts_user_id_alias(self, mock_channel_repository):
        controller = VoiceContextController(
            GetCurrentVoiceContextUseCase(mock_channel_repository)
        )
        request = Mock(spec=web.Request)
        request.query = {"user_id": "345678"}

        response = await controller.handle(request)

        assert response.status == 200
        assert "Mock Guild" in response.text

    async def test_handle_returns_not_found_when_member_not_in_voice(self):
        from tests.conftest import MockVoiceChannelRepository

        controller = VoiceContextController(
            GetCurrentVoiceContextUseCase(MockVoiceChannelRepository(return_none=True))
        )
        request = Mock(spec=web.Request)
        request.query = {"member_id": "345678"}

        response = await controller.handle(request)

        assert response.status == 404

    async def test_handle_requires_member_id(self, mock_channel_repository):
        controller = VoiceContextController(
            GetCurrentVoiceContextUseCase(mock_channel_repository)
        )
        request = Mock(spec=web.Request)
        request.query = {}

        response = await controller.handle(request)

        assert response.status == 400


class _FakeSpan:
    def set_attribute(self, key, value):
        del key, value


class _FakeSpanContext:
    def __enter__(self):
        return _FakeSpan()

    def __exit__(self, exc_type, exc, tb):
        del exc_type, exc, tb
        return False
