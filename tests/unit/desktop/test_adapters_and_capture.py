from types import SimpleNamespace

import pytest

from src.desktop.adapters import keyboard_backend, local_tts
from src.desktop.services.hotkey_capture import HotkeyTextCaptureSession


def test_pyttsx3_adapter_reports_availability_from_module_state(monkeypatch):
    monkeypatch.setattr(local_tts, "_pyttsx3_available", True)
    monkeypatch.setattr(local_tts, "pyttsx3", SimpleNamespace(init=lambda: object()))

    assert local_tts.Pyttsx3Adapter().is_available() is True
    assert local_tts.is_pyttsx3_available() is True


def test_pyttsx3_adapter_raises_when_library_is_unavailable(monkeypatch):
    monkeypatch.setattr(local_tts, "_pyttsx3_available", False)
    monkeypatch.setattr(local_tts, "pyttsx3", None)

    with pytest.raises(RuntimeError, match="pyttsx3 unavailable"):
        local_tts.Pyttsx3Adapter().create_engine()


def test_keyboard_hook_backend_delegates_to_keyboard_module(monkeypatch):
    calls = {"hook": [], "unhook_all": 0, "send": []}
    fake_keyboard = SimpleNamespace(
        hook=lambda callback: calls["hook"].append(callback),
        unhook_all=lambda: calls.__setitem__("unhook_all", calls["unhook_all"] + 1),
        send=lambda key: calls["send"].append(key),
    )
    callback = object()

    monkeypatch.setattr(keyboard_backend, "_keyboard_available", True)
    monkeypatch.setattr(keyboard_backend, "keyboard", fake_keyboard)

    backend = keyboard_backend.KeyboardHookBackend()
    backend.hook(callback)
    backend.unhook_all()
    backend.send_backspace()

    assert backend.is_available() is True
    assert keyboard_backend.is_keyboard_backend_available() is True
    assert calls["hook"] == [callback]
    assert calls["unhook_all"] == 1
    assert calls["send"] == ["backspace"]


def test_keyboard_hook_backend_handles_missing_library_gracefully(monkeypatch):
    monkeypatch.setattr(keyboard_backend, "_keyboard_available", False)
    monkeypatch.setattr(keyboard_backend, "keyboard", None)

    backend = keyboard_backend.KeyboardHookBackend()

    assert backend.is_available() is False
    assert keyboard_backend.is_keyboard_backend_available() is False
    backend.unhook_all()

    with pytest.raises(RuntimeError, match="keyboard backend unavailable"):
        backend.hook(lambda: None)

    with pytest.raises(RuntimeError, match="keyboard backend unavailable"):
        backend.send_backspace()


def test_hotkey_capture_session_returns_result_for_completed_text():
    session = HotkeyTextCaptureSession("{", "}")

    for key in ("{", "o", "l", "a"):
        assert session.process_key(key) is None

    result = session.process_key("}")

    assert result is not None
    assert result.text == "ola"
    assert result.backspace_count == 5
    assert result.trigger_open == "{"
    assert result.trigger_close == "}"


def test_hotkey_capture_session_supports_alias_keys_and_backspace():
    session = HotkeyTextCaptureSession("{", "}")

    for key in ("open_bracket", "o", "space", "x", "back", "right_bracket"):
        result = session.process_key(key)

    assert result is not None
    assert result.text == "o"
    assert result.backspace_count == 4


def test_hotkey_capture_session_ignores_empty_capture_and_reset_clears_state():
    session = HotkeyTextCaptureSession("{", "}")

    assert session.process_key("x") is None
    assert session.process_key("{") is None
    assert session.process_key("space") is None
    assert session.process_key("}") is None

    session.process_key("{")
    session.process_key("a")
    session.reset()

    assert session.process_key("}") is None


# pyright: reportArgumentType=false
