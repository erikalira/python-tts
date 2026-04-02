from unittest.mock import Mock

from src.application.tts_execution import (
    TTS_EXECUTION_RESULT_FAILED,
    TTS_EXECUTION_RESULT_MISSING_TEXT,
    TTS_EXECUTION_RESULT_OK,
)
from src.standalone.app.standalone_app import (
    StandaloneApplication,
    StandaloneHotkeyHandler,
    StandaloneTTSResultPresenter,
)
from src.standalone.config.standalone_config import StandaloneConfig
from src.standalone.services.hotkey_services import HotkeyEvent


def test_standalone_hotkey_handler_processes_captured_text():
    processor = Mock()
    presenter = Mock()
    handler = StandaloneHotkeyHandler(processor, presenter)
    event = HotkeyEvent(text="hello", character_count=7, trigger_open="{", trigger_close="}")

    handler.handle_text_captured(event)

    presenter.show_processing.assert_called_once_with("hello")
    processor.process_text.assert_called_once()
    assert processor.process_text.call_args.args == ("hello", 7)
    assert processor.process_text.call_args.kwargs["on_complete"] == presenter.present


def test_standalone_hotkey_handler_ignores_empty_text():
    processor = Mock()
    presenter = Mock()
    handler = StandaloneHotkeyHandler(processor, presenter)
    event = HotkeyEvent(text="", character_count=2, trigger_open="{", trigger_close="}")

    handler.handle_text_captured(event)

    presenter.show_processing.assert_not_called()
    processor.process_text.assert_not_called()


def test_standalone_tts_result_presenter_notifies_success_after_tts():
    notifier = Mock()
    presenter = StandaloneTTSResultPresenter(notifier)

    presenter.present({"success": True, "code": TTS_EXECUTION_RESULT_OK})

    notifier.notify_success.assert_called_once_with("TTS Hotkey", "Texto reproduzido com sucesso")


def test_standalone_tts_result_presenter_notifies_missing_text_error():
    notifier = Mock()
    presenter = StandaloneTTSResultPresenter(notifier)

    presenter.present({"success": False, "code": TTS_EXECUTION_RESULT_MISSING_TEXT})

    notifier.notify_error.assert_called_once_with("TTS Hotkey", "Nenhum texto valido foi capturado")


def test_standalone_tts_result_presenter_notifies_failure():
    notifier = Mock()
    presenter = StandaloneTTSResultPresenter(notifier)

    presenter.present({"success": False, "code": TTS_EXECUTION_RESULT_FAILED})

    notifier.notify_error.assert_called_once_with("TTS Hotkey", "Falha ao reproduzir o texto")


def test_standalone_tts_result_presenter_shows_processing_message():
    notifier = Mock()
    presenter = StandaloneTTSResultPresenter(notifier)

    presenter.show_processing("hello world")

    notifier.notify_info.assert_called_once()


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
