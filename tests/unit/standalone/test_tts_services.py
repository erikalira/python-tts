from types import SimpleNamespace
from unittest.mock import Mock

from src.standalone.config.standalone_config import StandaloneConfig
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


def test_discord_tts_service_builds_payload_and_sends_request(monkeypatch):
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000/"
    config.discord.channel_id = "10"
    config.discord.member_id = "20"

    response = SimpleNamespace(ok=True)
    post = Mock(return_value=response)
    monkeypatch.setattr("src.standalone.services.tts_services.requests.post", post)

    service = DiscordTTSService(config)

    assert service.speak("hello") is True
    call = post.call_args
    assert call.args[0] == "http://localhost:10000/speak"
    assert call.kwargs["json"]["text"] == "hello"
    assert call.kwargs["json"]["channel_id"] == "10"
    assert call.kwargs["json"]["member_id"] == "20"


def test_discord_tts_service_handles_http_error(monkeypatch):
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000"

    post = Mock(return_value=SimpleNamespace(ok=False, status_code=500))
    monkeypatch.setattr("src.standalone.services.tts_services.requests.post", post)

    assert DiscordTTSService(config).speak("hello") is False


def test_fallback_tts_engine_tries_next_available_engine():
    first = FakeEngine(available=True, result=False)
    second = FakeEngine(available=True, result=True)
    engine = FallbackTTSEngine([first, second])

    assert engine.speak("hello") is True
    assert first.calls == ["hello"]
    assert second.calls == ["hello"]


def test_tts_service_truncates_long_text(monkeypatch):
    config = StandaloneConfig.create_default()
    config.network.max_text_length = 5
    service = TTSService(config)
    engine = Mock()
    engine.speak.return_value = True
    service._engine = engine

    assert service.speak_text("abcdefgh") is True
    engine.speak.assert_called_once_with("abcde")


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

    monkeypatch.setattr("src.standalone.services.tts_services.pyttsx3.init", Mock(return_value=engine))

    local_engine = LocalPyTTSX3Engine(config)

    assert local_engine.speak("hello") is True
    engine.setProperty.assert_any_call("rate", config.tts.rate)
    engine.setProperty.assert_any_call("voice", "target-voice")
    engine.say.assert_called_once_with("hello")


def test_keyboard_cleanup_service_reports_suppression(monkeypatch):
    cleanup = KeyboardCleanupService()
    fake_keyboard = Mock()
    monkeypatch.setattr("sys.modules", {**__import__("sys").modules, "keyboard": fake_keyboard})

    cleanup.cleanup_typed_text(2)

    assert cleanup.is_suppressing_events() is False


def test_tts_processor_runs_cleanup_after_success(monkeypatch):
    processor = TTSProcessor(StandaloneConfig.create_default())
    processor._tts_service = Mock()
    processor._tts_service.speak_text.return_value = True
    processor._cleanup_service = Mock()

    class ImmediateThread:
        def __init__(self, target, daemon):
            self._target = target

        def start(self):
            self._target()

    monkeypatch.setattr("src.standalone.services.tts_services.threading.Thread", ImmediateThread)

    processor.process_text("hello", cleanup_count=3)

    processor._tts_service.speak_text.assert_called_once_with("hello")
    processor._cleanup_service.cleanup_typed_text.assert_called_once_with(3)
