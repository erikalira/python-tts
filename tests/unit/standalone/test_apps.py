from unittest.mock import Mock

from src.standalone.app.standalone_app import StandaloneApplication, StandaloneHotkeyHandler
from src.standalone.config.standalone_config import StandaloneConfig
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


def test_standalone_application_handle_configure_updates_services():
    app = StandaloneApplication()
    app._config = StandaloneConfig.create_default()
    app._config_service = Mock()
    updated_config = StandaloneConfig.create_default()
    updated_config.discord.member_id = "123"
    app._config_service.get_configuration.return_value = updated_config
    app._config_repository = Mock()
    app._notification_service = Mock()
    app._update_services_config = Mock()

    app._handle_configure()

    app._config_repository.save.assert_called_once_with(updated_config)
    app._update_services_config.assert_called_once()
    app._notification_service.notify_success.assert_called_once()


def test_standalone_application_handle_configure_rejects_invalid_config():
    app = StandaloneApplication()
    app._config = StandaloneConfig.create_default()
    app._config_service = Mock()
    invalid_config = StandaloneConfig.create_default()
    invalid_config.discord.member_id = "abc"
    app._config_service.get_configuration.return_value = invalid_config
    app._config_repository = Mock()
    app._notification_service = Mock()
    app._update_services_config = Mock()

    app._handle_configure()

    app._config_repository.save.assert_not_called()
    app._update_services_config.assert_not_called()
    app._notification_service.notify_error.assert_called_once()
