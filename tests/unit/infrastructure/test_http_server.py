"""Tests for aiohttp HTTP server endpoints."""
import pytest
from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from unittest.mock import AsyncMock, Mock

from src.infrastructure.http.server import HTTPServer


@pytest.mark.asyncio
async def test_http_server_exposes_health_version_and_about_routes():
    speak_handler = AsyncMock()
    voice_context_handler = AsyncMock()
    server = HTTPServer(
        speak_handler=speak_handler,
        voice_context_handler=voice_context_handler,
        port=10000,
    )

    app = server._build_app()
    for path in ("/health", "/version", "/about", "/voice-context"):
        request = make_mocked_request("GET", path, app=app)
        match_info = await app.router.resolve(request)
        response = await match_info.handler(request)

        if path == "/voice-context":
            voice_context_handler.assert_awaited_once_with(request)
            continue

        assert response.status == 200

        if path == "/health":
            assert response.text == '{"status": "healthy"}'
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
