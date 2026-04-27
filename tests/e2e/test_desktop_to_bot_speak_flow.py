import asyncio
from unittest.mock import AsyncMock, Mock

import pytest
from aiohttp import web

from src.application.dto import SPEAK_RESULT_QUEUED, SpeakTextResult
from src.application.use_cases import SpeakTextUseCase
from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.services.discord_bot_client import HttpDiscordBotClient
from src.infrastructure.http.server import HTTPServer
from src.presentation.http_controllers import SpeakController


@pytest.mark.asyncio
async def test_desktop_client_posts_speak_request_to_bot_http_endpoint():
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
    controller = SpeakController(use_case, auth_token="e2e-token", max_text_length=500)
    http_server = HTTPServer(
        speak_handler=controller.handle,
        voice_context_handler=AsyncMock(return_value=web.json_response({"success": True, "code": "ok"})),
        port=0,
    )
    app = http_server._build_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 0)

    try:
        await site.start()
        socket = site._server.sockets[0]
        port = socket.getsockname()[1]

        config = DesktopAppConfig.create_default()
        config.discord.bot_url = f"http://127.0.0.1:{port}"
        config.discord.member_id = "123"
        config.discord.speak_token = "e2e-token"
        config.tts.engine = "edge-tts"
        config.tts.language = "pt-BR"
        config.tts.voice_id = "pt-BR-FranciscaNeural"
        config.tts.rate = 210

        client = HttpDiscordBotClient(config)
        accepted = await asyncio.to_thread(client.send_text, "hello from desktop")

        assert accepted is True
        assert client.get_last_error_message() is None
        use_case.execute.assert_awaited_once()
        speak_input = use_case.execute.await_args.args[0]
        assert speak_input.text == "hello from desktop"
        assert speak_input.member_id == 123
        assert speak_input.config_override is not None
        assert speak_input.config_override.engine == "edge-tts"
    finally:
        await runner.cleanup()
