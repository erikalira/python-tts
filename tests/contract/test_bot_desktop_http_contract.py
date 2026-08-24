import json
from dataclasses import replace
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

from src.application.dto import (
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_QUEUED,
    VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL,
    VOICE_CONTEXT_RESULT_OK,
    SpeakTextResult,
    VoiceContextResult,
)
from src.application.dto.contracts import BotHealthResponseDTO, BotVoiceContextResponseDTO
from src.application.rate_limiting import RateLimitResult
from src.application.use_cases import GetCurrentVoiceContextUseCase, SpeakTextUseCase
from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.services.discord_bot_client import DiscordBotHttpTransport, HttpDiscordBotClient
from src.infrastructure.http.server import HTTPServer
from src.infrastructure.rate_limiting import InMemoryRateLimiter
from src.presentation.http_controllers import SpeakController, VoiceContextController


@pytest.mark.asyncio
async def test_speak_contract_accepts_authenticated_json_request():
    use_case = Mock(spec=SpeakTextUseCase)
    use_case.execute = AsyncMock(
        return_value=SpeakTextResult(
            success=True,
            code=SPEAK_RESULT_QUEUED,
            queued=True,
            position=0,
            queue_size=1,
        )
    )
    controller = SpeakController(use_case, auth_token="contract-token")
    request = _speak_request(
        headers={"X-Bot-Token": "contract-token"},
        payload={"text": "hello", "member_id": "123", "guild_id": 456, "channel_id": 789},
    )

    response = await controller.handle(request)

    assert response.status == 200
    assert response.text == "queued at position 1/1"


@pytest.mark.asyncio
async def test_speak_contract_rejects_missing_auth_token():
    use_case = Mock(spec=SpeakTextUseCase)
    use_case.execute = AsyncMock(
        return_value=SpeakTextResult(success=True, code=SPEAK_RESULT_QUEUED, queued=True, position=0)
    )
    controller = SpeakController(use_case, auth_token="contract-token")
    request = _speak_request(payload={"text": "hello", "member_id": "123"})

    response = await controller.handle(request)

    assert response.status == 401
    assert response.text == "unauthorized"
    use_case.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_speak_contract_rejects_invalid_content_type():
    controller = SpeakController(Mock(spec=SpeakTextUseCase), auth_token="contract-token")
    request = _speak_request(
        headers={"X-Bot-Token": "contract-token"},
        payload={"text": "hello"},
        content_type="text/plain",
    )

    response = await controller.handle(request)

    assert response.status == 415
    assert response.text == "unsupported media type"


@pytest.mark.asyncio
async def test_speak_contract_rejects_oversized_text():
    controller = SpeakController(
        Mock(spec=SpeakTextUseCase),
        auth_token="contract-token",
        max_text_length=5,
    )
    request = _speak_request(
        headers={"X-Bot-Token": "contract-token"},
        payload={"text": "too long"},
    )

    response = await controller.handle(request)

    assert response.status == 413
    assert response.text == "text too long"


@pytest.mark.asyncio
async def test_speak_contract_rejects_rate_limited_caller():
    use_case = Mock(spec=SpeakTextUseCase)
    use_case.execute = AsyncMock(
        return_value=SpeakTextResult(success=True, code=SPEAK_RESULT_QUEUED, queued=True, position=0)
    )
    controller = SpeakController(
        use_case,
        auth_token="contract-token",
        rate_limiter=InMemoryRateLimiter(clock=lambda: 100.0),
        rate_limit_max_requests=1,
        rate_limit_window_seconds=10,
    )
    request = _speak_request(
        headers={"X-Bot-Token": "contract-token"},
        payload={"text": "hello", "guild_id": 456, "member_id": "123"},
    )

    first_response = await controller.handle(request)
    second_response = await controller.handle(request)

    assert first_response.status == 200
    assert second_response.status == 429
    assert second_response.text == "rate limit exceeded; retry after 10 seconds"


@pytest.mark.asyncio
async def test_speak_contract_reports_queue_failure():
    use_case = Mock(spec=SpeakTextUseCase)
    use_case.execute = AsyncMock(
        return_value=SpeakTextResult(success=False, code=SPEAK_RESULT_QUEUE_FULL, queued=False)
    )
    controller = SpeakController(use_case, auth_token="contract-token")
    request = _speak_request(
        headers={"X-Bot-Token": "contract-token"},
        payload={"text": "hello", "member_id": "123"},
    )

    response = await controller.handle(request)

    assert response.status == 400
    assert response.text == "audio queue is full"


@pytest.mark.asyncio
async def test_health_and_readiness_contracts_are_json():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
        readiness_provider=AsyncMock(return_value={"status": "ready", "dependencies": []}),
    )
    app = server._build_app()

    health = await _route(app, "GET", "/health")
    ready = await _route(app, "GET", "/ready")

    assert health.status == 200
    assert health.text == '{"status": "healthy"}'
    assert ready.status == 200
    assert ready.text == '{"status": "ready", "dependencies": []}'


def test_rate_limit_retry_without_retry_after_keeps_contract_message():
    presenter_result = RateLimitResult(allowed=False, scope="contract")

    controller = SpeakController(Mock(spec=SpeakTextUseCase))
    response_text = controller._presenter.build_rate_limit_message(presenter_result)

    assert response_text == "rate limit exceeded"


def _speak_request(
    *,
    payload: object,
    headers: dict[str, str] | None = None,
    content_type: str = "application/json",
) -> Mock:
    request = Mock(spec=web.Request)
    request.headers = headers or {}
    request.content_type = content_type
    request.json = AsyncMock(return_value=payload)
    return request


async def _route(app: web.Application, method: str, path: str) -> web.StreamResponse:
    request = make_mocked_request(method, path, app=app)
    match_info = await app.router.resolve(request)
    return await match_info.handler(request)


# ---------------------------------------------------------------------------
# Consumer side of the contract.
#
# The tests above assert what the bot *produces*. These assert that the desktop
# client, which is deployed and versioned separately, can still *consume* it.
# Both halves must be exercised: a response-shape change that only breaks the
# desktop would otherwise pass CI and fail at runtime.
# ---------------------------------------------------------------------------


class _FakeResponse:
    """Minimal stand-in for a requests.Response, as the desktop parsers see it."""

    def __init__(self, payload: object, *, status_code: int = 200, text: str = ""):
        self._payload = payload
        self.status_code = status_code
        self.ok = 200 <= status_code < 300
        self.text = text

    def json(self):
        if self._payload is _NO_JSON:
            raise ValueError("no json body")
        return self._payload


_NO_JSON = object()


def _desktop_transport() -> DiscordBotHttpTransport:
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "20"
    return DiscordBotHttpTransport(config)


@pytest.mark.asyncio
async def test_desktop_parses_bot_health_payload():
    """The bot's real /health body must satisfy the desktop's health parser."""
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
        readiness_provider=AsyncMock(return_value={"status": "ready", "dependencies": []}),
    )
    health = await _route(server._build_app(), "GET", "/health")

    parsed = _desktop_transport()._parse_health_payload(_FakeResponse(json.loads(health.text)))

    assert isinstance(parsed, BotHealthResponseDTO)
    assert parsed.status == "healthy"


@pytest.mark.asyncio
async def test_desktop_parses_bot_voice_context_success_payload():
    """A successful /voice-context body must round-trip into the desktop DTO."""
    use_case = Mock(spec=GetCurrentVoiceContextUseCase)
    use_case.execute = AsyncMock(
        return_value=VoiceContextResult(
            success=True,
            code=VOICE_CONTEXT_RESULT_OK,
            member_id=20,
            guild_id=456,
            guild_name="Guild",
            channel_id=789,
            channel_name="General",
        )
    )
    controller = VoiceContextController(use_case)
    request = make_mocked_request("GET", "/voice-context?member_id=20")

    response = await controller.handle(request)
    parsed = _desktop_transport()._parse_voice_context_payload(_FakeResponse(json.loads(response.text)))

    assert response.status == 200
    assert isinstance(parsed, BotVoiceContextResponseDTO)
    assert parsed.success is True
    assert parsed.code == VOICE_CONTEXT_RESULT_OK
    assert parsed.member_id == 20
    assert parsed.guild_id == 456
    assert parsed.guild_name == "Guild"
    assert parsed.channel_id == 789
    assert parsed.channel_name == "General"


@pytest.mark.asyncio
async def test_desktop_parses_voice_context_not_in_channel_payload():
    """The presenter drops None fields; the desktop must tolerate absent keys."""
    use_case = Mock(spec=GetCurrentVoiceContextUseCase)
    use_case.execute = AsyncMock(
        return_value=VoiceContextResult(success=False, code=VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL, member_id=20)
    )
    controller = VoiceContextController(use_case)

    response = await controller.handle(make_mocked_request("GET", "/voice-context?member_id=20"))
    payload = json.loads(response.text)
    parsed = _desktop_transport()._parse_voice_context_payload(_FakeResponse(payload, status_code=404))

    assert response.status == 404
    assert "guild_id" not in payload  # presenter strips None
    assert isinstance(parsed, BotVoiceContextResponseDTO)
    assert parsed.success is False
    assert parsed.code == VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL
    assert parsed.guild_id is None
    assert parsed.message == "user is not connected to a voice channel"


@pytest.mark.asyncio
async def test_desktop_speak_request_is_accepted_by_bot_controller():
    """The desktop's outgoing payload must satisfy the bot's speak parser."""
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "20"
    config.discord.speak_token = "contract-token"
    config.tts = replace(config.tts, engine="edge-tts", language="pt-BR", voice_id="pt-BR-Francisca", rate=210)

    desktop_payload = HttpDiscordBotClient(config).build_request("hello").to_payload()

    use_case = Mock(spec=SpeakTextUseCase)
    use_case.execute = AsyncMock(
        return_value=SpeakTextResult(success=True, code=SPEAK_RESULT_QUEUED, queued=True, position=0, queue_size=1)
    )
    controller = SpeakController(use_case, auth_token="contract-token")
    response = await controller.handle(
        _speak_request(headers={"X-Bot-Token": "contract-token"}, payload=desktop_payload)
    )

    assert response.status == 200
    speak_input = use_case.execute.await_args.args[0]
    assert speak_input.text == "hello"
    assert speak_input.member_id == 20
    # TTSConfig field names are the wire protocol between the two deployables.
    assert speak_input.config_override is not None
    assert speak_input.config_override.engine == "edge-tts"
    assert speak_input.config_override.language == "pt-BR"
    assert speak_input.config_override.voice_id == "pt-BR-Francisca"
    assert speak_input.config_override.rate == 210


def test_desktop_handles_non_json_error_body():
    """The bot returns plain text on 401/429; the parser must not explode."""
    transport = _desktop_transport()

    assert transport._parse_health_payload(_FakeResponse(_NO_JSON, status_code=401, text="unauthorized")) is None
    assert transport._parse_voice_context_payload(_FakeResponse(_NO_JSON, status_code=429)) is None
