from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request

from src.application.dto import SPEAK_RESULT_QUEUE_FULL, SPEAK_RESULT_QUEUED, SpeakTextResult
from src.application.rate_limiting import RateLimitResult
from src.application.use_cases import SpeakTextUseCase
from src.infrastructure.http.server import HTTPServer
from src.infrastructure.rate_limiting import InMemoryRateLimiter
from src.presentation.http_controllers import SpeakController


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
