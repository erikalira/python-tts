from types import SimpleNamespace
from unittest.mock import ANY, Mock

from src.application.dto import DesktopTTSServiceStatusDTO, DesktopTTSStatusDTO
from src.application.desktop_tts import DesktopTTSFlowService, DesktopTTSStatusUseCase
from src.application.desktop_bot import DesktopBotConnectionStatus, DesktopBotVoiceContextStatus
from src.application.tts_execution import (
    SpeakTextExecutionUseCase,
    TTS_EXECUTION_RESULT_FAILED,
    TTS_EXECUTION_RESULT_MISSING_TEXT,
    TTS_EXECUTION_RESULT_OK,
    TTSExecutionResult,
)
from src.application.tts_routing import build_tts_engine_chain
from src.desktop.app.tts_runtime import DesktopAppTTSProcessor
from src.desktop.config.desktop_config import DesktopAppConfig, get_default_discord_bot_url
from src.desktop.services.discord_bot_client import DiscordSpeakRequestDTO, HttpDiscordBotClient
from src.desktop.services.tts_services import (
    DesktopAppTTSService,
    DiscordTTSService,
    KeyboardCleanupService,
    LocalPyTTSX3Engine,
)


class FakeEngine:
    def __init__(self, available=True, result=True):
        self.available = available
        self.result = result
        self.calls = []

    def is_available(self):
        return self.available

    def speak(self, text):
        self.calls.append(text)
        return self.result


class FakeDiscordBotClient:
    def __init__(self, available=True, result=True, last_error_message=None):
        self.available = available
        self.result = result
        self.last_error_message = last_error_message
        self.requests = []

    def is_available(self):
        return self.available

    def build_request(self, text):
        return DiscordSpeakRequestDTO(text=text, member_id="20")

    def send_speak_request(self, request):
        self.requests.append(request)
        return self.result

    def get_last_error_message(self):
        return self.last_error_message


def test_http_discord_bot_client_builds_payload_and_url():
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url().rstrip("/") + "/"
    config.discord.member_id = "20"
    config.tts.engine = "edge-tts"
    config.tts.language = "pt-BR"
    config.tts.voice_id = "pt-BR-FranciscaNeural"
    config.tts.rate = 210

    client = HttpDiscordBotClient(config)
    request = client.build_request("hello")

    assert request.to_payload() == {
        "text": "hello",
        "member_id": "20",
        "config_override": {
            "engine": "edge-tts",
            "language": "pt-BR",
            "voice_id": "pt-BR-FranciscaNeural",
            "rate": 210,
        },
    }
    assert client.get_speak_url() == get_default_discord_bot_url().rstrip("/") + "/speak"
    assert client.get_health_url() == get_default_discord_bot_url().rstrip("/") + "/health"


def test_discord_tts_service_builds_payload_and_sends_request():
    config = DesktopAppConfig.create_default()
    config.tts.engine = "pyttsx3"
    config.tts.language = "system"
    config.tts.voice_id = "David"
    bot_client = FakeDiscordBotClient(available=True, result=True)
    service = DiscordTTSService(config, bot_client=bot_client)

    assert service.speak("hello") is True
    assert len(bot_client.requests) == 1
    assert bot_client.requests[0].to_payload() == {"text": "hello", "member_id": "20"}


def test_discord_tts_service_handles_http_error():
    config = DesktopAppConfig.create_default()
    bot_client = FakeDiscordBotClient(available=True, result=False)
    assert DiscordTTSService(config, bot_client=bot_client).speak("hello") is False


def test_http_discord_bot_client_handles_http_error(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()

    post = Mock(return_value=SimpleNamespace(ok=False, status_code=500, text="playback failed"))
    monkeypatch.setattr("src.desktop.services.discord_bot_client.requests.post", post)

    client = HttpDiscordBotClient(config)

    assert client.send_speak_request(client.build_request("hello")) is False
    assert client.get_last_error_message() == "Bot respondeu HTTP 500: playback failed"


def test_http_discord_bot_client_simplifies_service_suspended_error(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()

    response = SimpleNamespace(
        ok=False,
        status_code=503,
        text="<!DOCTYPE html><html><body>Service Suspended</body></html>",
    )
    post = Mock(return_value=response)
    monkeypatch.setattr("src.desktop.services.discord_bot_client.requests.post", post)

    client = HttpDiscordBotClient(config)

    assert client.send_speak_request(client.build_request("hello")) is False
    assert client.get_last_error_message() == "Bot respondeu HTTP 503: servico suspenso ou indisponivel"


def test_http_discord_bot_client_check_connection_success(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()

    get = Mock(return_value=SimpleNamespace(ok=True, status_code=200))
    monkeypatch.setattr("src.desktop.services.discord_bot_client.requests.get", get)

    result = HttpDiscordBotClient(config).check_connection()

    assert result.success is True
    assert "sucesso" in result.message.lower()


def test_http_discord_bot_client_check_connection_http_failure(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()

    get = Mock(return_value=SimpleNamespace(ok=False, status_code=503))
    monkeypatch.setattr("src.desktop.services.discord_bot_client.requests.get", get)

    result = HttpDiscordBotClient(config).check_connection()

    assert result == DesktopBotConnectionStatus(success=False, message="Bot respondeu HTTP 503")


def test_http_discord_bot_client_fetches_voice_context(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = "20"

    get = Mock(
        return_value=SimpleNamespace(
            ok=True,
            status_code=200,
            json=lambda: {
                "success": True,
                "guild_name": "Guild A",
                "guild_id": 30,
                "channel_name": "Sala 1",
                "channel_id": 10,
            },
        )
    )
    monkeypatch.setattr("src.desktop.services.discord_bot_client.requests.get", get)

    result = HttpDiscordBotClient(config).fetch_voice_context()

    assert result == DesktopBotVoiceContextStatus(
        success=True,
        message="Canal detectado: Guild A / Sala 1",
        guild_name="Guild A",
        guild_id=30,
        channel_name="Sala 1",
        channel_id=10,
    )


def test_http_discord_bot_client_reports_when_user_not_in_voice(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = "20"

    get = Mock(
        return_value=SimpleNamespace(
            ok=False,
            status_code=404,
            json=lambda: {"success": False, "code": "not_in_channel"},
        )
    )
    monkeypatch.setattr("src.desktop.services.discord_bot_client.requests.get", get)

    result = HttpDiscordBotClient(config).fetch_voice_context()

    assert result == DesktopBotVoiceContextStatus(
        success=False,
        message="Usuario nao esta conectado a nenhum canal de voz",
    )


def test_http_discord_bot_client_reports_when_voice_context_endpoint_is_missing(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = "20"

    get = Mock(
        return_value=SimpleNamespace(
            ok=False,
            status_code=404,
            json=lambda: {},
        )
    )
    monkeypatch.setattr("src.desktop.services.discord_bot_client.requests.get", get)

    result = HttpDiscordBotClient(config).fetch_voice_context()

    assert result == DesktopBotVoiceContextStatus(
        success=False,
        message="Endpoint de deteccao de canal nao esta disponivel no bot. Atualize o bot.",
    )


def test_desktop_tts_flow_service_tries_next_available_engine():
    first = FakeEngine(available=True, result=False)
    second = FakeEngine(available=True, result=True)
    flow = DesktopTTSFlowService(
        preferred_engine="discord",
        discord_engine=first,
        local_engine=second,
        max_text_length=500,
    )

    assert flow.speak_text("hello") is True
    assert first.calls == ["hello"]
    assert second.calls == ["hello"]


def test_build_tts_engine_chain_prefers_local_engine_when_configured():
    local = FakeEngine()
    discord = FakeEngine()

    chain = build_tts_engine_chain("pyttsx3", discord_engine=discord, local_engine=local)

    assert chain == [local, discord]


def test_desktop_app_tts_service_prefers_local_engine_when_configured():
    config = DesktopAppConfig.create_default()
    config.tts.engine = "pyttsx3"
    config.interface.local_tts_enabled = True
    bot_client = FakeDiscordBotClient(available=True, result=True)
    local_engine = FakeEngine(available=True, result=True)
    service = DesktopAppTTSService(
        config,
        bot_client=bot_client,
        local_engine_factory=lambda cfg: local_engine,
    )

    assert service.speak_text("hello") is True
    assert local_engine.calls == ["hello"]
    assert bot_client.requests == []


def test_desktop_app_tts_service_uses_discord_when_local_voice_is_disabled():
    config = DesktopAppConfig.create_default()
    config.tts.engine = "pyttsx3"
    config.interface.local_tts_enabled = False
    bot_client = FakeDiscordBotClient(available=True, result=True)
    local_engine = FakeEngine(available=True, result=True)
    service = DesktopAppTTSService(
        config,
        bot_client=bot_client,
        local_engine_factory=lambda cfg: local_engine,
    )

    assert service.speak_text("hello") is True
    assert local_engine.calls == []
    assert len(bot_client.requests) == 1


def test_desktop_app_tts_service_delegates_to_flow_service():
    config = DesktopAppConfig.create_default()
    service = DesktopAppTTSService(config, bot_client=FakeDiscordBotClient())
    flow_service = Mock()
    flow_service.speak_text.return_value = True
    service._flow_service = flow_service

    assert service.speak_text("abcdefgh") is True
    flow_service.speak_text.assert_called_once_with("abcdefgh")


def test_desktop_app_tts_service_returns_false_for_blank_text():
    service = DesktopAppTTSService(
        DesktopAppConfig.create_default(),
        bot_client=FakeDiscordBotClient(),
    )
    flow_service = Mock()
    flow_service.speak_text.return_value = False
    service._flow_service = flow_service

    assert service.speak_text("   ") is False
    flow_service.speak_text.assert_called_once_with("   ")


def test_local_pyttsx3_engine_initializes_and_speaks():
    config = DesktopAppConfig.create_default()
    config.tts.voice_id = "target"

    engine = Mock()
    engine.say = Mock()
    engine.runAndWait = Mock()

    adapter = Mock()
    adapter.is_available.return_value = True
    adapter.create_configured_engine.return_value = engine

    local_engine = LocalPyTTSX3Engine(config, adapter=adapter)

    assert local_engine.speak("hello") is True
    adapter.create_configured_engine.assert_called_once_with(config.tts, ANY)
    engine.say.assert_called_once_with("hello")


def test_desktop_app_tts_service_reports_local_voice_as_disabled_by_default():
    config = DesktopAppConfig.create_default()

    status = DesktopAppTTSService(config, bot_client=FakeDiscordBotClient()).get_status_info()

    assert status.local_tts_enabled is False
    assert status.local_available is False


def test_desktop_app_tts_service_exposes_status_contract_without_private_access():
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.interface.local_tts_enabled = True
    bot_client = FakeDiscordBotClient(available=True, result=True)
    bot_client.has_transport = Mock(return_value=True)
    local_engine = FakeEngine(available=True, result=True)
    service = DesktopAppTTSService(
        config,
        bot_client=bot_client,
        local_engine_factory=lambda cfg: local_engine,
    )

    assert service.is_remote_available() is True
    assert service.is_local_enabled() is True
    assert service.is_local_available() is True
    assert service.has_transport() is True
    assert service.has_bot_url() is True


def test_desktop_tts_status_use_case_builds_status_payload():
    gateway = Mock()
    gateway.is_remote_available.return_value = True
    gateway.is_local_enabled.return_value = True
    gateway.is_local_available.return_value = True
    gateway.is_local_dependency_installed.return_value = True
    gateway.has_transport.return_value = True
    gateway.has_bot_url.return_value = True

    status = DesktopTTSStatusUseCase(gateway).execute()

    assert status == DesktopTTSStatusDTO(
        discord_available=True,
        local_tts_enabled=True,
        local_available=True,
        pyttsx3_installed=True,
        requests_installed=True,
        bot_url_configured=True,
    )


def test_keyboard_cleanup_service_reports_suppression():
    backend = Mock()
    backend.is_available.return_value = True
    cleanup = KeyboardCleanupService(keyboard_backend=backend)

    cleanup.cleanup_typed_text(2)

    assert cleanup.is_suppressing_events() is False
    assert backend.send_backspace.call_count == 2


def test_speak_text_execution_use_case_delegates_to_tts_service():
    tts_service = Mock()
    tts_service.speak_text.return_value = True
    tts_service.is_available.return_value = True
    tts_service.get_status_info.return_value = DesktopTTSStatusDTO(
        discord_available=False,
        local_tts_enabled=True,
        local_available=True,
        pyttsx3_installed=True,
        requests_installed=False,
        bot_url_configured=False,
    )
    tts_service.get_last_error_message.return_value = None

    execution = SpeakTextExecutionUseCase(tts_service)

    result = execution.execute("hello")

    assert result == TTSExecutionResult(success=True, code=TTS_EXECUTION_RESULT_OK)
    assert execution.is_available() is True
    assert execution.get_status_info() == DesktopTTSStatusDTO(
        discord_available=False,
        local_tts_enabled=True,
        local_available=True,
        pyttsx3_installed=True,
        requests_installed=False,
        bot_url_configured=False,
    )
    tts_service.speak_text.assert_called_once_with("hello")


def test_speak_text_execution_use_case_normalizes_text_before_delegating():
    tts_service = Mock()
    tts_service.speak_text.return_value = True
    tts_service.is_available.return_value = True
    tts_service.get_status_info.return_value = DesktopTTSStatusDTO(
        discord_available=False,
        local_tts_enabled=False,
        local_available=False,
        pyttsx3_installed=False,
        requests_installed=False,
        bot_url_configured=False,
    )
    tts_service.get_last_error_message.return_value = None

    execution = SpeakTextExecutionUseCase(tts_service)

    result = execution.execute("  hello  ")

    assert result == TTSExecutionResult(success=True, code=TTS_EXECUTION_RESULT_OK)
    tts_service.speak_text.assert_called_once_with("hello")


def test_speak_text_execution_use_case_returns_missing_text_without_calling_service():
    tts_service = Mock()
    execution = SpeakTextExecutionUseCase(tts_service)

    result = execution.execute("   ")

    assert result == TTSExecutionResult(success=False, code=TTS_EXECUTION_RESULT_MISSING_TEXT)
    tts_service.speak_text.assert_not_called()


def test_speak_text_execution_use_case_returns_failure_when_tts_service_fails():
    tts_service = Mock()
    tts_service.speak_text.return_value = False
    tts_service.get_last_error_message.return_value = "Bot respondeu HTTP 503: servico suspenso ou indisponivel"
    execution = SpeakTextExecutionUseCase(tts_service)

    result = execution.execute("hello")

    assert result == TTSExecutionResult(
        success=False,
        code=TTS_EXECUTION_RESULT_FAILED,
        message="Bot respondeu HTTP 503: servico suspenso ou indisponivel",
    )


def test_desktop_app_tts_processor_runs_cleanup_after_success(monkeypatch):
    execution_service = Mock()
    execution_service.execute.return_value = TTSExecutionResult(
        success=True,
        code=TTS_EXECUTION_RESULT_OK,
    )
    cleanup_service = Mock()
    on_complete = Mock()
    processor = DesktopAppTTSProcessor(
        execution_service=execution_service,
        cleanup_service=cleanup_service,
    )

    class ImmediateThread:
        def __init__(self, target, daemon):
            self._target = target

        def start(self):
            self._target()

    monkeypatch.setattr("src.desktop.app.tts_runtime.threading.Thread", ImmediateThread)

    processor.process_text("hello", cleanup_count=3, on_complete=on_complete)

    execution_service.execute.assert_called_once_with("hello")
    cleanup_service.cleanup_typed_text.assert_called_once_with(3)
    on_complete.assert_called_once_with(
        TTSExecutionResult(success=True, code=TTS_EXECUTION_RESULT_OK)
    )


def test_desktop_app_tts_processor_skips_cleanup_when_execution_fails(monkeypatch):
    execution_service = Mock()
    execution_service.execute.return_value = TTSExecutionResult(
        success=False,
        code=TTS_EXECUTION_RESULT_FAILED,
    )
    cleanup_service = Mock()
    on_complete = Mock()
    processor = DesktopAppTTSProcessor(
        execution_service=execution_service,
        cleanup_service=cleanup_service,
    )

    class ImmediateThread:
        def __init__(self, target, daemon):
            self._target = target

        def start(self):
            self._target()

    monkeypatch.setattr("src.desktop.app.tts_runtime.threading.Thread", ImmediateThread)

    processor.process_text("hello", cleanup_count=3, on_complete=on_complete)

    execution_service.execute.assert_called_once_with("hello")
    cleanup_service.cleanup_typed_text.assert_not_called()
    on_complete.assert_called_once_with(
        TTSExecutionResult(success=False, code=TTS_EXECUTION_RESULT_FAILED)
    )
