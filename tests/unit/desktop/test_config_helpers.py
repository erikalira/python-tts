from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.gui.config_helpers import (
    build_updated_config,
    normalize_optional_text,
    prompt_numeric_input,
    resolve_text_value,
    validate_numeric_field,
)


def test_normalize_optional_text_returns_none_for_blank_value():
    assert normalize_optional_text("   ") is None


def test_normalize_optional_text_returns_stripped_value():
    assert normalize_optional_text("  123  ") == "123"


def test_resolve_text_value_uses_fallback_for_blank_value():
    assert resolve_text_value("   ", "fallback") == "fallback"


def test_resolve_text_value_returns_stripped_text():
    assert resolve_text_value("  hello  ", "fallback") == "hello"


def test_prompt_numeric_input_retries_until_numeric(monkeypatch, capsys):
    responses = iter(["abc", "42"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

    result = prompt_numeric_input("Discord User ID: ", "", "only numbers")

    assert result == "42"
    assert "only numbers" in capsys.readouterr().out


def test_prompt_numeric_input_keeps_current_value_when_blank(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _prompt: "   ")

    result = prompt_numeric_input("Discord User ID: ", "123", "only numbers")

    assert result == "123"


def test_validate_numeric_field_requires_value_when_configured_as_required():
    result = validate_numeric_field(
        "   ",
        required=True,
        required_message="required",
        numeric_message="numeric",
    )

    assert result == "required"


def test_validate_numeric_field_rejects_non_numeric_text():
    result = validate_numeric_field(
        "abc",
        required=False,
        required_message="required",
        numeric_message="numeric",
    )

    assert result == "numeric"


def test_validate_numeric_field_accepts_blank_optional_value():
    result = validate_numeric_field(
        "   ",
        required=False,
        required_message="required",
        numeric_message="numeric",
    )

    assert result is None


def test_build_updated_config_preserves_existing_values_for_none_fields():
    current = DesktopAppConfig.create_default()
    current.discord.member_id = "123"
    current.discord.bot_url = "http://bot"
    current.tts.engine = "gtts"
    current.tts.language = "pt"
    current.tts.voice_id = "voice"
    current.tts.rate = 180
    current.hotkey.trigger_open = "{"
    current.hotkey.trigger_close = "}"
    current.interface.show_notifications = True
    current.interface.console_logs = True
    current.interface.local_tts_enabled = False

    updated = build_updated_config(current)

    assert updated is not current
    assert updated.discord.member_id == "123"
    assert updated.discord.bot_url == "http://bot"
    assert updated.tts.engine == "gtts"
    assert updated.tts.language == "pt"
    assert updated.tts.voice_id == "voice"
    assert updated.tts.rate == 180
    assert updated.hotkey.trigger_open == "{"
    assert updated.hotkey.trigger_close == "}"
    assert updated.interface.show_notifications is True
    assert updated.interface.console_logs is True
    assert updated.interface.local_tts_enabled is False
    assert updated.network is current.network


def test_build_updated_config_applies_new_values():
    current = DesktopAppConfig.create_default()

    updated = build_updated_config(
        current,
        member_id="456",
        bot_url="http://new-bot",
        engine="pyttsx3",
        language="en",
        voice_id="voice-2",
        rate=220,
        trigger_open="[",
        trigger_close="]",
        show_notifications=False,
        console_logs=False,
        local_tts_enabled=True,
    )

    assert updated.discord.member_id == "456"
    assert updated.discord.bot_url == "http://new-bot"
    assert updated.tts.engine == "pyttsx3"
    assert updated.tts.language == "en"
    assert updated.tts.voice_id == "voice-2"
    assert updated.tts.rate == 220
    assert updated.hotkey.trigger_open == "["
    assert updated.hotkey.trigger_close == "]"
    assert updated.interface.show_notifications is False
    assert updated.interface.console_logs is False
    assert updated.interface.local_tts_enabled is True
