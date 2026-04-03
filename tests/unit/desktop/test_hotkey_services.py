from types import SimpleNamespace
from unittest.mock import Mock

from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.services.hotkey_services import (
    HotkeyManager,
    StandardKeyboardMonitor,
)


def test_standard_keyboard_monitor_captures_text_sequence():
    config = DesktopAppConfig.create_default()
    handler = Mock()
    monitor = StandardKeyboardMonitor(config, handler)

    monitor._process_key("{")
    monitor._process_key("o")
    monitor._process_key("l")
    monitor._process_key("a")
    monitor._process_key("}")

    handler.handle_text_captured.assert_called_once()
    event = handler.handle_text_captured.call_args.args[0]
    assert event.text == "ola"
    assert event.character_count == 5


def test_standard_keyboard_monitor_handles_space_and_backspace():
    config = DesktopAppConfig.create_default()
    handler = Mock()
    monitor = StandardKeyboardMonitor(config, handler)

    for key in ("{", "o", "space", "x", "backspace", "}"):
        monitor._process_key(key)

    event = handler.handle_text_captured.call_args.args[0]
    assert event.text == "o"


def test_standard_keyboard_monitor_ignores_non_keydown():
    config = DesktopAppConfig.create_default()
    handler = Mock()
    monitor = StandardKeyboardMonitor(config, handler)

    monitor._backend = SimpleNamespace(is_available=lambda: True, key_down_event="down")

    monitor._on_key_event(SimpleNamespace(event_type="up", name="{"))

    handler.handle_text_captured.assert_not_called()


def test_standard_keyboard_monitor_respects_suppression():
    config = DesktopAppConfig.create_default()
    handler = Mock()
    monitor = StandardKeyboardMonitor(config, handler)
    monitor.set_external_suppression_check(lambda: True)

    monitor._backend = SimpleNamespace(is_available=lambda: True, key_down_event="down")

    monitor._on_key_event(SimpleNamespace(event_type="down", name="{"))

    handler.handle_text_captured.assert_not_called()


def test_hotkey_manager_update_config_restarts_active_service():
    config = DesktopAppConfig.create_default()
    new_config = DesktopAppConfig.create_default()
    new_config.hotkey.trigger_open = "["
    handler = Mock()

    replacement_service = Mock()
    replacement_service.start.return_value = True
    factory = Mock(side_effect=[Mock(), replacement_service])
    manager = HotkeyManager(config, service_factory=factory)
    manager.initialize(handler)

    service = Mock()
    service.is_active.return_value = True
    manager._service = service

    manager.update_config(new_config)

    service.stop.assert_called_once()
    assert manager._config.hotkey.trigger_open == "["
    assert manager._service is replacement_service
    replacement_service.start.assert_called_once()


def test_hotkey_manager_status_before_initialization():
    manager = HotkeyManager(DesktopAppConfig.create_default())

    status = manager.get_status()

    assert status["initialized"] is False
    assert status["active"] is False

