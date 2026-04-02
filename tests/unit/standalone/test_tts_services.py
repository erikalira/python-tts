from types import SimpleNamespace
from unittest.mock import Mock

from src.application.tts_execution import (
    SpeakTextExecutionUseCase,
    TTS_EXECUTION_RESULT_FAILED,
    TTS_EXECUTION_RESULT_MISSING_TEXT,
    TTS_EXECUTION_RESULT_OK,
)
from src.application.tts_routing import build_tts_engine_chain
from src.standalone.config.standalone_config import StandaloneConfig
from src.standalone.services.discord_bot_client import DiscordSpeakRequest, HttpDiscordBotClient
from src.standalone.services.tts_services import (
    DiscordTTSService,
    FallbackTTSEngine,
    KeyboardCleanupService,
    LocalPyTTSX3Engine,
    TTSProcessor,
    TTSService,
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
    def __init__(self, available=True, result=True):
        self.available = available
        self.result = result
        self.requests = []

    def is_available(self):
        return self.available

    def build_request(self, text):
        return DiscordSpeakRequest(text=text, guild_id="30", channel_id="10", member_id="20")

    def send_speak_request(self, request):
        self.requests.append(request)
        return self.result


def test_http_discord_bot_client_builds_payload_and_url():
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000/"
    config.discord.guild_id = "30"
    config.discord.channel_id = "10"
    config.discord.member_id = "20"

    client = HttpDiscordBotClient(config)
    request = client.build_request("hello")

    assert request.to_payload() == {"text": "hello", "guild_id": "30", "channel_id": "10", "member_id": "20"}
    assert client.get_speak_url() == "http://localhost:10000/speak"


def test_discord_tts_service_builds_payload_and_sends_request(monkeypatch):
    config = StandaloneConfig.create_default()
    bot_client = FakeDiscordBotClient(available=True, result=True)
    service = DiscordTTSService(config, bot_client=bot_client)

    assert service.speak("hello") is True
    assert len(bot_client.requests) == 1
    assert bot_client.requests[0].to_payload() == {"text": "hello", "guild_id": "30", "channel_id": "10", "member_id": "20"}


def test_discord_tts_service_handles_http_error(monkeypatch):
    config = StandaloneConfig.create_default()
    bot_client = FakeDiscordBotClient(available=True, result=False)
    assert DiscordTTSService(config, bot_client=bot_client).speak("hello") is False


def test_http_discord_bot_client_handles_http_error(monkeypatch):
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000"

    post = Mock(return_value=SimpleNamespace(ok=False, status_code=500))
    monkeypatch.setattr("src.standalone.services.discord_bot_client.requests.post", post)

    client = HttpDiscordBotClient(config)

    assert client.send_speak_request(client.build_request("hello")) is False


def test_fallback_tts_engine_tries_next_available_engine():
    first = FakeEngine(available=True, result=False)
    second = FakeEngine(available=True, result=True)
    engine = FallbackTTSEngine([first, second])

    assert engine.speak("hello") is True
    assert first.calls == ["hello"]
    assert second.calls == ["hello"]


def test_build_tts_engine_chain_prefers_local_engine_when_configured():
    local = FakeEngine()
    discord = FakeEngine()

    chain = build_tts_engine_chain("pyttsx3", discord_engine=discord, local_engine=local)

    assert chain == [local, discord]


def test_tts_service_prefers_local_engine_when_configured():
    config = StandaloneConfig.create_default()
    config.tts.engine = "pyttsx3"
    bot_client = FakeDiscordBotClient(available=True, result=True)
    local_engine = FakeEngine(available=True, result=True)
    service = TTSService(
        config,
        bot_client=bot_client,
        local_engine_factory=lambda cfg: local_engine,
    )

    assert service.speak_text("hello") is True
    assert local_engine.calls == ["hello"]
    assert bot_client.requests == []


def test_tts_service_truncates_long_text(monkeypatch):
    config = StandaloneConfig.create_default()
    config.network.max_text_length = 5
    service = TTSService(config, bot_client=FakeDiscordBotClient())
    engine = Mock()
    engine.speak.return_value = True
    service._engine = engine

    assert service.speak_text("abcdefgh") is True
    engine.speak.assert_called_once_with("abcde")


def test_tts_service_strips_whitespace_before_speaking():
    config = StandaloneConfig.create_default()
    service = TTSService(config, bot_client=FakeDiscordBotClient())
    engine = Mock()
    engine.speak.return_value = True
    service._engine = engine

    assert service.speak_text("  hello  ") is True
    engine.speak.assert_called_once_with("hello")


def test_tts_service_returns_false_for_blank_text():
    service = TTSService(StandaloneConfig.create_default())
    assert service.speak_text("   ") is False


def test_local_pyttsx3_engine_initializes_and_speaks(monkeypatch):
    config = StandaloneConfig.create_default()
    config.tts.voice_id = "target"

    voice = SimpleNamespace(id="target-voice")
    engine = Mock()
    engine.getProperty.return_value = [voice]
    engine.say = Mock()
    engine.runAndWait = Mock()

    adapter = Mock()
    adapter.is_available.return_value = True
    adapter.create_engine.return_value = engine

    local_engine = LocalPyTTSX3Engine(config, adapter=adapter)

    assert local_engine.speak("hello") is True
    engine.setProperty.assert_any_call("rate", config.tts.rate)
    engine.setProperty.assert_any_call("voice", "target-voice")
    engine.say.assert_called_once_with("hello")


def test_keyboard_cleanup_service_reports_suppression(monkeypatch):
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
    tts_service.get_status_info.return_value = {"local_available": True}

    execution = SpeakTextExecutionUseCase(tts_service)

    result = execution.execute("hello")

    assert result == {"success": True, "code": TTS_EXECUTION_RESULT_OK}
    assert execution.is_available() is True
    assert execution.get_status_info() == {"local_available": True}
    tts_service.speak_text.assert_called_once_with("hello")


def test_speak_text_execution_use_case_returns_missing_text_without_calling_service():
    tts_service = Mock()
    execution = SpeakTextExecutionUseCase(tts_service)

    result = execution.execute("   ")

    assert result == {"success": False, "code": TTS_EXECUTION_RESULT_MISSING_TEXT}
    tts_service.speak_text.assert_not_called()


def test_speak_text_execution_use_case_returns_failure_when_tts_service_fails():
    tts_service = Mock()
    tts_service.speak_text.return_value = False
    execution = SpeakTextExecutionUseCase(tts_service)

    result = execution.execute("hello")

    assert result == {"success": False, "code": TTS_EXECUTION_RESULT_FAILED}


def test_tts_processor_runs_cleanup_after_success(monkeypatch):
    execution_service = Mock()
    execution_service.execute.return_value = {"success": True, "code": TTS_EXECUTION_RESULT_OK}
    cleanup_service = Mock()
    processor = TTSProcessor(
        StandaloneConfig.create_default(),
        execution_service=execution_service,
        cleanup_service=cleanup_service,
    )

    class ImmediateThread:
        def __init__(self, target, daemon):
            self._target = target

        def start(self):
            self._target()

    monkeypatch.setattr("src.standalone.services.tts_services.threading.Thread", ImmediateThread)

    processor.process_text("hello", cleanup_count=3)

    execution_service.execute.assert_called_once_with("hello")
    cleanup_service.cleanup_typed_text.assert_called_once_with(3)


def test_tts_processor_skips_cleanup_when_execution_fails(monkeypatch):
    execution_service = Mock()
    execution_service.execute.return_value = {"success": False, "code": TTS_EXECUTION_RESULT_FAILED}
    cleanup_service = Mock()
    processor = TTSProcessor(
        StandaloneConfig.create_default(),
        execution_service=execution_service,
        cleanup_service=cleanup_service,
    )

    class ImmediateThread:
        def __init__(self, target, daemon):
            self._target = target

        def start(self):
            self._target()

    monkeypatch.setattr("src.standalone.services.tts_services.threading.Thread", ImmediateThread)

    processor.process_text("hello", cleanup_count=3)

    execution_service.execute.assert_called_once_with("hello")
    cleanup_service.cleanup_typed_text.assert_not_called()
