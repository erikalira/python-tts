from unittest.mock import AsyncMock, Mock

from scripts.test.quality_gates import evaluate_observability_payload, load_quality_gate_config
from src.desktop.app.desktop_app import DesktopApp
from src.desktop.config.desktop_config import DesktopAppConfig
from src.infrastructure.http.server import HTTPServer
from src.infrastructure.runtime_observability import InMemoryBotRuntimeTelemetry
from src.core.entities import AudioQueueItem, TTSRequest


def test_bot_health_endpoint_smoke():
    server = HTTPServer(
        speak_handler=AsyncMock(),
        voice_context_handler=AsyncMock(),
        port=10000,
        observability_snapshot_provider=lambda: {"status": "enabled"},
    )

    app = server._build_app()

    assert app.router["health"].url_for().human_repr() == "/health"
    assert app.router["observability"].url_for().human_repr() == "/observability"


def test_desktop_runtime_startup_and_minimum_flow_smoke(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "123"

    config_repository = Mock()
    config_repository.load.return_value = config

    config_service = Mock()

    tts_processor = Mock()
    tts_processor.is_processing.return_value = False

    hotkey_manager = Mock()
    hotkey_manager.start.return_value = True
    hotkey_manager.is_active.return_value = True

    notification_service = Mock()
    notification_service.start.return_value = True
    notification_service.is_running.return_value = False
    notification_service.is_available.return_value = True

    app = DesktopApp(
        config_repository=config_repository,
        config_service=config_service,
        tts_processor_factory=lambda cfg: tts_processor,
        hotkey_manager_factory=lambda cfg: hotkey_manager,
        notification_service_factory=lambda cfg: notification_service,
        console_wait_factory=lambda: Mock(is_available=lambda: False),
    )

    fake_gateway = Mock()
    fake_gateway.has_bot_url.return_value = True
    fake_gateway.check_connection.return_value = Mock(success=True, message="ok")
    fake_gateway.has_member_id.return_value = True
    fake_gateway.send_text.return_value = True
    monkeypatch.setattr(app, "_bot_gateway_factory", lambda cfg: fake_gateway)

    assert app.initialize() is True
    assert app._start_services() is True

    connection_result = app._test_bot_connection(config)
    send_result = app._send_test_message(config)

    assert connection_result.success is True
    assert send_result.success is True


def test_bot_observability_sli_baseline_smoke():
    config = load_quality_gate_config("config/quality_gates.json")
    telemetry = InMemoryBotRuntimeTelemetry()

    for index, latency_ms in enumerate((900.0, 1100.0, 1300.0, 1800.0, 2200.0), start=1):
        request = TTSRequest(text=f"texto-{index}", guild_id=1, member_id=index)
        telemetry.record_submission_result(
            request=request,
            accepted=True,
            code="queued",
            engine="gtts",
        )
        item = AudioQueueItem(request=request, created_at=100.0 + index)
        item.mark_completed()
        item.completed_at = item.created_at + (latency_ms / 1000.0)
        telemetry.record_processing_result(item=item, success=True, code="ok", engine="gtts")

    failures = evaluate_observability_payload(telemetry.snapshot_payload(), config.sli)

    assert failures == []
