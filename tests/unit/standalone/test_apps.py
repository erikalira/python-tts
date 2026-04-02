from unittest.mock import Mock

from src.standalone.app.simple_app import SimpleHotkeyHandler
from src.standalone.app.standalone_app import StandaloneHotkeyHandler
from src.standalone.services.hotkey_services import HotkeyEvent


def test_standalone_hotkey_handler_processes_captured_text():
    processor = Mock()
    notifier = Mock()
    handler = StandaloneHotkeyHandler(processor, notifier)
    event = HotkeyEvent(text="hello", character_count=7, trigger_open="{", trigger_close="}")

    handler.handle_text_captured(event)

    notifier.notify_info.assert_called_once()
    processor.process_text.assert_called_once_with("hello", 7)


def test_standalone_hotkey_handler_ignores_empty_text():
    processor = Mock()
    notifier = Mock()
    handler = StandaloneHotkeyHandler(processor, notifier)
    event = HotkeyEvent(text="", character_count=2, trigger_open="{", trigger_close="}")

    handler.handle_text_captured(event)

    notifier.notify_info.assert_not_called()
    processor.process_text.assert_not_called()


def test_simple_hotkey_handler_processes_captured_text():
    processor = Mock()
    notifier = Mock()
    handler = SimpleHotkeyHandler(processor, notifier)
    event = HotkeyEvent(text="hello", character_count=7, trigger_open="{", trigger_close="}")

    handler.handle_text_captured(event)

    notifier.notify_info.assert_called_once()
    processor.process_text.assert_called_once_with("hello", 7)
