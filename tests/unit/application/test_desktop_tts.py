from unittest.mock import Mock

from src.application.desktop_tts import DesktopTTSFlowService, DesktopTTSStatusUseCase
from src.application.dto import DesktopTTSStatusDTO


class FakeEngine:
    def __init__(self, *, available=True, result=True):
        self._available = available
        self._result = result
        self.calls = []

    def speak(self, text: str) -> bool:
        self.calls.append(text)
        return self._result

    def is_available(self) -> bool:
        return self._available


def test_desktop_tts_flow_service_ignores_blank_text():
    engine = FakeEngine()
    flow_service = DesktopTTSFlowService(
        preferred_engine="discord",
        discord_engine=engine,
        local_engine=None,
        max_text_length=50,
    )

    assert flow_service.speak_text("   ") is False
    assert engine.calls == []


def test_desktop_tts_flow_service_truncates_text_before_speaking():
    engine = FakeEngine()
    flow_service = DesktopTTSFlowService(
        preferred_engine="discord",
        discord_engine=engine,
        local_engine=None,
        max_text_length=5,
    )

    assert flow_service.speak_text("abcdefgh") is True
    assert engine.calls == ["abcde"]


def test_desktop_tts_flow_service_reports_unavailable_when_no_engine_is_available():
    discord_engine = FakeEngine(available=False)
    local_engine = FakeEngine(available=False)
    flow_service = DesktopTTSFlowService(
        preferred_engine="discord",
        discord_engine=discord_engine,
        local_engine=local_engine,
        max_text_length=50,
    )

    assert flow_service.is_available() is False


def test_desktop_tts_status_use_case_builds_status_payload():
    gateway = Mock()
    gateway.is_remote_available.return_value = True
    gateway.is_local_enabled.return_value = True
    gateway.is_local_available.return_value = False
    gateway.is_local_dependency_installed.return_value = True
    gateway.has_transport.return_value = True
    gateway.has_bot_url.return_value = False

    status = DesktopTTSStatusUseCase(gateway).execute()

    assert status == DesktopTTSStatusDTO(
        discord_available=True,
        local_tts_enabled=True,
        local_available=False,
        pyttsx3_installed=True,
        requests_installed=True,
        bot_url_configured=False,
    )
