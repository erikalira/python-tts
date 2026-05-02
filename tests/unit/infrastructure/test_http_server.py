"""Tests for aiohttp HTTP server endpoints."""
import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from unittest.mock import AsyncMock

from src.infrastructure.http.server import HTTPServer


@pytest.mark.asyncio
async def test_http_server_exposes_health_version_and_about_routes():
    speak_handler = AsyncMock()
    voice_context_handler = AsyncMock()
    server = HTTPServer(
        speak_handler=speak_handler,
        voice_context_handler=voice_context_handler,
        port=10000,
        observability_snapshot_provider=lambda: {"status": "enabled", "total_requests": 3},
        readiness_provider=AsyncMock(return_value={"status": "ready", "dependencies": []}),
    )

    app = server._build_app()
    for path in ("/health", "/ready", "/observability", "/version", "/about", "/voice-context"):
        request = make_mocked_request("GET", path, app=app)
        match_info = await app.router.resolve(request)
        response = await match_info.handler(request)

        if path == "/voice-context":
            voice_context_handler.assert_awaited_once_with(request)
            continue

        assert response.status == 200

        if path == "/health":
            assert response.text == '{"status": "healthy"}'
        elif path == "/ready":
            assert response.text == '{"status": "ready", "dependencies": []}'
        elif path == "/observability":
            assert '"status": "enabled"' in response.text
            assert '"total_requests": 3' in response.text
        elif path == "/version":
            assert "version" in response.text
            assert "author" in response.text
        else:
            assert '"status": "online"' in response.text
            assert '"name": "Discord Bot and Desktop App"' in response.text


@pytest.mark.asyncio
async def test_http_server_routes_speak_to_controller():
    speak_handler = AsyncMock(return_value=web.Response(text="ok"))
    voice_context_handler = AsyncMock()
    server = HTTPServer(
        speak_handler=speak_handler,
        voice_context_handler=voice_context_handler,
        port=10000,
    )

    app = server._build_app()
    request = make_mocked_request("POST", "/speak", app=app)
    match_info = await app.router.resolve(request)

    response = await match_info.handler(request)

    assert response.status == 200
    speak_handler.assert_awaited_once_with(request)


def test_http_server_configures_max_request_body_size():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
        max_request_body_bytes=2048,
    )

    app = server._build_app()

    assert app._client_max_size == 2048


@pytest.mark.asyncio
async def test_http_server_applies_cors_headers_for_allowed_origin():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
        cors_allowed_origins=("http://localhost:5173",),
    )

    request = make_mocked_request(
        "POST",
        "/speak",
        headers={"Origin": "http://localhost:5173"},
    )
    response = web.Response(text="ok")

    server._apply_cors_headers(request, response)

    assert response.headers["Access-Control-Allow-Origin"] == "http://localhost:5173"
    assert response.headers["Access-Control-Allow-Methods"] == "POST, OPTIONS"
    assert "Authorization" in response.headers["Access-Control-Allow-Headers"]
    assert response.headers["Vary"] == "Origin"


@pytest.mark.asyncio
async def test_http_server_does_not_apply_cors_headers_for_unlisted_origin():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
        cors_allowed_origins=("http://localhost:5173",),
    )

    request = make_mocked_request(
        "POST",
        "/speak",
        headers={"Origin": "https://example.invalid"},
    )
    response = web.Response(text="ok")

    server._apply_cors_headers(request, response)

    assert "Access-Control-Allow-Origin" not in response.headers


@pytest.mark.asyncio
async def test_http_server_rejects_speak_preflight_for_unlisted_origin():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
        cors_allowed_origins=("http://localhost:5173",),
    )
    app = server._build_app()
    request = make_mocked_request(
        "OPTIONS",
        "/speak",
        app=app,
        headers={"Origin": "https://example.invalid"},
    )
    match_info = await app.router.resolve(request)

    response = await match_info.handler(request)

    assert response.status == 403
    assert response.text == "cors origin not allowed"


@pytest.mark.asyncio
async def test_http_server_returns_disabled_observability_when_provider_is_missing():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
    )

    app = server._build_app()
    request = make_mocked_request("GET", "/observability", app=app)
    match_info = await app.router.resolve(request)

    response = await match_info.handler(request)

    assert response.status == 200
    assert response.text == '{"status": "disabled"}'


@pytest.mark.asyncio
async def test_http_server_returns_503_when_readiness_provider_is_missing():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
    )

    app = server._build_app()
    request = make_mocked_request("GET", "/ready", app=app)
    match_info = await app.router.resolve(request)

    response = await match_info.handler(request)

    assert response.status == 503
    assert response.text == '{"status": "unknown", "dependencies": []}'


@pytest.mark.asyncio
async def test_http_server_returns_503_when_readiness_provider_reports_not_ready():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
        readiness_provider=AsyncMock(
            return_value={
                "status": "not_ready",
                "dependencies": [{"name": "redis", "status": "not_ready", "required": True}],
            }
        ),
    )

    app = server._build_app()
    request = make_mocked_request("GET", "/ready", app=app)
    match_info = await app.router.resolve(request)

    response = await match_info.handler(request)

    assert response.status == 503
    assert '"status": "not_ready"' in response.text
# pyright: reportAttributeAccessIssue=false
