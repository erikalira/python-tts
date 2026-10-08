"""Tests for HTTP controllers."""

from typing import Any, cast
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp import web

from src.application.dto import SpeakTextResult
from src.application.rate_limiting import RateLimitResult
from src.application.use_cases import GetCurrentVoiceContextUseCase, SpeakTextUseCase
from src.core.entities import TTSConfig
from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime
from src.infrastructure.rate_limiting import InMemoryRateLimiter
from src.presentation.http_controllers import SpeakController, VoiceContextController


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
        request.json = AsyncMock(
            return_value={"text": "Hello world", "guild_id": 789012, "channel_id": 123456, "member_id": 345678}
        )

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
        request.json = AsyncMock(return_value={"text": ""})

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
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
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
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
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
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
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
        request.json = AsyncMock(
            return_value={"text": "Hello world", "channel_id": 123456, "guild_id": 789012, "member_id": 345678}
        )

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
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012, "user_id": 345678})

        response = await controller.handle(request)

        assert response.status == 200

    async def test_handle_rate_limits_by_guild_and_member(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
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
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
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
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
        controller = SpeakController(use_case, auth_token="secret")
        request = Mock(spec=web.Request)
        request.headers = {"X-Bot-Token": "secret"}
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012, "member_id": 345678})

        response = await controller.handle(request)

        assert response.status == 200
        use_case.execute.assert_awaited_once()

    async def test_handle_accepts_bearer_auth_token(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
        controller = SpeakController(use_case, auth_token="secret")
        request = Mock(spec=web.Request)
        request.headers = {"Authorization": "Bearer secret"}
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012, "member_id": 345678})

        response = await controller.handle(request)

        assert response.status == 200
        use_case.execute.assert_awaited_once()

    async def test_handle_injects_trace_context_when_otel_is_available(self):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
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
        controller = VoiceContextController(GetCurrentVoiceContextUseCase(mock_channel_repository))
        request = Mock(spec=web.Request)
        request.query = {"member_id": "345678"}

        response = await controller.handle(request)

        assert response.status == 200
        assert "Mock Guild" in response.text
        assert "Mock Voice" in response.text

    async def test_handle_accepts_user_id_alias(self, mock_channel_repository):
        controller = VoiceContextController(GetCurrentVoiceContextUseCase(mock_channel_repository))
        request = Mock(spec=web.Request)
        request.query = {"user_id": "345678"}

        response = await controller.handle(request)

        assert response.status == 200
        assert "Mock Guild" in response.text

    async def test_handle_returns_not_found_when_member_not_in_voice(self):
        from tests.conftest import MockVoiceChannelRepository

        controller = VoiceContextController(GetCurrentVoiceContextUseCase(MockVoiceChannelRepository(return_none=True)))
        request = Mock(spec=web.Request)
        request.query = {"member_id": "345678"}

        response = await controller.handle(request)

        assert response.status == 404

    async def test_handle_requires_member_id(self, mock_channel_repository):
        controller = VoiceContextController(GetCurrentVoiceContextUseCase(mock_channel_repository))
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


# pyright: reportOperatorIssue=false, reportOptionalMemberAccess=false


class TestSpeakControllerConfigOverrideValidation:
    """The /speak override must be validated like /config is.

    Before Fish Audio every engine was keyless, so an unvalidated engine
    override cost nothing. A caller holding BOT_SPEAK_TOKEN could otherwise
    drive the operator's credentialed provider account with an arbitrary voice.
    """

    def _controller(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        return SpeakController(use_case)

    async def test_rejects_unknown_engine_override(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        controller = self._controller(
            mock_tts_engine, mock_channel_repository, mock_config_repository, mock_audio_queue, build_speak_use_case
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={"text": "hi", "guild_id": 1, "engine": "totally-made-up"})

        response = await controller.handle(request)

        assert response.status == 400
        assert "Unsupported engine override" in response.text
        # The value the caller sent must not be reflected back into the body.
        assert "totally-made-up" not in response.text
        assert mock_tts_engine.calls == []

    async def test_rejects_fish_audio_override_with_malformed_voice_id(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        controller = self._controller(
            mock_tts_engine, mock_channel_repository, mock_config_repository, mock_audio_queue, build_speak_use_case
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(
            return_value={"text": "hi", "guild_id": 1, "engine": "fish-audio", "voice_id": "not-hex"}
        )

        response = await controller.handle(request)

        assert response.status == 400
        assert "voice_id" in response.text
        assert mock_tts_engine.calls == []

    async def test_accepts_fish_audio_override_with_valid_reference_id(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        controller = self._controller(
            mock_tts_engine, mock_channel_repository, mock_config_repository, mock_audio_queue, build_speak_use_case
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(
            return_value={
                "text": "hi",
                "guild_id": 789012,
                "channel_id": 123456,
                "member_id": 345678,
                "engine": "fish-audio",
                "voice_id": "0123456789abcdef0123456789abcdef",
            }
        )

        response = await controller.handle(request)

        assert response.status == 200
        # Status alone would stay green if the override were silently ignored
        # and the stored base config used instead.
        assert mock_audio_queue.items
        override = mock_audio_queue.items[-1].request.config_override
        assert override is not None
        assert override.engine == "fish-audio"
        assert override.voice_id == "0123456789abcdef0123456789abcdef"


class TestSpeakControllerOverrideEdgeCases:
    """Cases the first pass of override validation missed."""

    def _controller(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        return SpeakController(use_case)

    async def test_validation_applies_inside_the_nested_override_form(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """The controller reads data["config_override"] first, so test that shape."""
        controller = self._controller(
            mock_tts_engine, mock_channel_repository, mock_config_repository, mock_audio_queue, build_speak_use_case
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(
            return_value={
                "text": "hi",
                "guild_id": 1,
                "config_override": {"engine": "fish-audio", "voice_id": "not-hex"},
            }
        )

        response = await controller.handle(request)

        assert response.status == 400
        assert mock_tts_engine.calls == []

    async def test_voice_only_override_is_validated_against_the_stored_engine(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """resolved_engine comes from the base config when none is sent."""
        mock_config_repository.set_config(
            1,
            TTSConfig(engine="fish-audio", language="pt", voice_id="0123456789abcdef0123456789abcdef", rate=180),
        )
        controller = self._controller(
            mock_tts_engine, mock_channel_repository, mock_config_repository, mock_audio_queue, build_speak_use_case
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={"text": "hi", "guild_id": 1, "voice_id": "bogus"})

        response = await controller.handle(request)

        assert response.status == 400
        assert mock_tts_engine.calls == []

    async def test_fish_override_voice_id_is_stripped_before_use(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """What was validated must be what is transmitted."""
        controller = self._controller(
            mock_tts_engine, mock_channel_repository, mock_config_repository, mock_audio_queue, build_speak_use_case
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(
            return_value={
                "text": "hi",
                "guild_id": 789012,
                "channel_id": 123456,
                "member_id": 345678,
                "engine": "fish-audio",
                "voice_id": "  0123456789abcdef0123456789abcdef\n",
            }
        )

        response = await controller.handle(request)

        assert response.status == 200
        override = mock_audio_queue.items[-1].request.config_override
        assert override.voice_id == "0123456789abcdef0123456789abcdef"

    @pytest.mark.parametrize("engine", ["gtts", "pyttsx3", "edge-tts"])
    async def test_existing_engines_still_accepted_as_overrides(
        self,
        engine,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """Regression: the new gate must not reject the three keyless engines."""
        controller = self._controller(
            mock_tts_engine, mock_channel_repository, mock_config_repository, mock_audio_queue, build_speak_use_case
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(
            return_value={
                "text": "hi",
                "guild_id": 789012,
                "channel_id": 123456,
                "member_id": 345678,
                "engine": engine,
            }
        )

        response = await controller.handle(request)

        assert response.status == 200
        assert mock_audio_queue.items[-1].request.config_override.engine == engine


class TestRateLimitPrecedesOverrideValidation:
    """The reject path must cost budget, so it cannot be driven for free."""

    def _controller(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
        rate_limiter=None,
    ):
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        if rate_limiter is None:
            return SpeakController(use_case)
        return SpeakController(use_case, rate_limiter=rate_limiter)

    async def test_invalid_override_consumes_one_unit_of_budget(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        calls: list = []

        class _CountingLimiter:
            def check(self, request):
                calls.append(request)
                return RateLimitResult(allowed=True, scope="test")

        controller = self._controller(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository,
            mock_audio_queue,
            build_speak_use_case,
            rate_limiter=_CountingLimiter(),
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={"text": "hi", "guild_id": 1, "engine": "nope"})

        response = await controller.handle(request)

        assert response.status == 400
        assert len(calls) == 1

    async def test_exhausted_budget_wins_over_an_invalid_override(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """A caller over budget gets the rate-limit answer, not the 400."""

        class _BlockingLimiter:
            def check(self, request):
                return RateLimitResult(allowed=False, scope="test", retry_after_seconds=3)

        controller = self._controller(
            mock_tts_engine,
            mock_channel_repository,
            mock_config_repository,
            mock_audio_queue,
            build_speak_use_case,
            rate_limiter=_BlockingLimiter(),
        )
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={"text": "hi", "guild_id": 1, "engine": "nope"})

        response = await controller.handle(request)

        assert response.status != 400
        assert mock_tts_engine.calls == []


class TestConfigOverrideErrorDoesNotLeakInternals:
    """Only text authored in this module may reach a 400 body.

    Catching bare ValueError would also catch one raised inside the config
    repository and relay its internals to an external caller - the exposure
    CodeQL flagged on PR #86.
    """

    async def test_repository_valueerror_is_not_reflected(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        class _ExplodingRepository:
            def get_config(self, guild_id=None, user_id=None):
                raise ValueError("internal detail: /secret/path/db.sqlite row 42")

        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=cast(Any, _ExplodingRepository()),
            mock_audio_queue=mock_audio_queue,
        )
        controller = SpeakController(use_case, config_repository=cast(Any, _ExplodingRepository()))
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={"text": "hi", "guild_id": 1, "engine": "gtts"})

        try:
            response = await controller.handle(request)
        except ValueError:
            # Propagating is acceptable: aiohttp answers 500 with no body detail.
            return

        assert "secret" not in response.text
        assert "db.sqlite" not in response.text

    async def test_authored_message_is_still_reflected(
        self,
        mock_tts_engine,
        mock_channel_repository,
        mock_config_repository,
        mock_audio_queue,
        build_speak_use_case,
    ):
        """The actionable detail Gard approved must survive the hardening."""
        use_case = build_speak_use_case(
            mock_tts_engine=mock_tts_engine,
            mock_channel_repository=mock_channel_repository,
            mock_config_repository=mock_config_repository,
            mock_audio_queue=mock_audio_queue,
        )
        controller = SpeakController(use_case)
        request = Mock(spec=web.Request)
        request.json = AsyncMock(return_value={"text": "hi", "guild_id": 1, "engine": "fish-audio", "voice_id": "nope"})

        response = await controller.handle(request)

        assert response.status == 400
        assert "32-character hexadecimal" in response.text


class TestBearerTokenParsing:
    """Malformed Authorization headers had no coverage.

    The scheme check and the empty-value check are separate rejections, and
    neither was exercised: only the happy path and the missing-header path were.
    """

    @pytest.mark.parametrize(
        "header",
        ["Basic secret", "Bearer", "Bearer    ", "Token secret", "secret"],
    )
    async def test_malformed_authorization_header_is_rejected(self, header):
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
        controller = SpeakController(use_case, auth_token="secret")
        request = Mock(spec=web.Request)
        request.headers = {"Authorization": header}
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012})

        response = await controller.handle(request)

        assert response.status == 401
        use_case.execute.assert_not_awaited()

    async def test_lowercase_bearer_scheme_is_accepted(self):
        """RFC 7235 makes the scheme case-insensitive."""
        use_case = Mock(spec=SpeakTextUseCase)
        use_case.execute = AsyncMock(return_value=SpeakTextResult(success=True, code="queued", queued=True, position=0))
        controller = SpeakController(use_case, auth_token="secret")
        request = Mock(spec=web.Request)
        request.headers = {"Authorization": "bearer secret"}
        request.json = AsyncMock(return_value={"text": "Hello", "guild_id": 789012})

        response = await controller.handle(request)

        assert response.status == 200
