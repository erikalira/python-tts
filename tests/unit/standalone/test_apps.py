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


def test_standalone_application_handle_configure_pauses_hotkeys_while_gui_is_open():
    app = StandaloneApplication()
    app._config = StandaloneConfig.create_default()
    app._config_service = Mock()
    updated_config = StandaloneConfig.create_default()
    updated_config.discord.member_id = "123"
    updated_config.discord.guild_id = "456"
    app._config_service.get_configuration.return_value = updated_config
    app._config_repository = Mock()
    app._notification_service = Mock()
    app._update_services_config = Mock()
    app._hotkey_manager = Mock()
    app._hotkey_manager.is_active.side_effect = [True, False]

    app._handle_configure()

    app._hotkey_manager.stop.assert_called_once()
    assert app._hotkey_manager.start.call_count == 1


def test_standalone_application_update_services_config_rebuilds_hotkey_manager():
    app = StandaloneApplication(
        tts_processor_factory=Mock(return_value=Mock()),
        hotkey_manager_factory=Mock(side_effect=[Mock(), Mock()]),
        notification_service_factory=Mock(side_effect=[Mock(), Mock()]),
    )
    app._config = StandaloneConfig.create_default()
    app._tts_processor = Mock()
    app._hotkey_manager = Mock()
    app._hotkey_manager.is_active.return_value = False
    app._notification_service = Mock()
    app._notification_service.is_available.return_value = False

    app._update_services_config()

    assert app._hotkey_manager is not None
    app._hotkey_manager.initialize.assert_called_once()


def test_standalone_application_save_configuration_from_ui_applies_changes():
    app = StandaloneApplication()
    updated_config = StandaloneConfig.create_default()
    updated_config.discord.bot_url = "http://localhost:10000"
    updated_config.discord.guild_id = "456"
    updated_config.discord.member_id = "123"
    app._config = StandaloneConfig.create_default()
    app._config_repository = Mock()
    app._update_services_config = Mock()

    result = app._save_configuration_from_ui(updated_config)

    assert result["success"] is True
    app._config_repository.save.assert_called_once_with(updated_config)
    app._update_services_config.assert_called_once()


def test_standalone_application_test_bot_connection_uses_http_client(monkeypatch):
    app = StandaloneApplication()
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000"

    fake_client = Mock()
    fake_client.check_connection.return_value = {"success": True, "message": "ok"}
    monkeypatch.setattr("src.standalone.app.standalone_app.HttpDiscordBotClient", lambda cfg: fake_client)

    result = app._test_bot_connection(config)

    assert result == {"success": True, "message": "ok"}
    fake_client.check_connection.assert_called_once_with()


def test_standalone_application_send_test_message_requires_discord_identifiers():
    app = StandaloneApplication()
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000"
    config.discord.guild_id = None
    config.discord.member_id = None

    result = app._send_test_message(config)

    assert result["success"] is False
    assert "Guild ID" in result["message"]


def test_standalone_application_send_test_message_uses_http_client(monkeypatch):
    app = StandaloneApplication()
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000"
    config.discord.guild_id = "456"
    config.discord.member_id = "123"

    fake_request = Mock()
    fake_client = Mock()
    fake_client.build_request.return_value = fake_request
    fake_client.send_speak_request.return_value = True
    monkeypatch.setattr("src.standalone.app.standalone_app.HttpDiscordBotClient", lambda cfg: fake_client)

    result = app._send_test_message(config)

    assert result == {"success": True, "message": "Mensagem de teste enviada ao bot com sucesso"}
    fake_client.build_request.assert_called_once_with("Teste rápido do TTS Hotkey.")
    fake_client.send_speak_request.assert_called_once_with(fake_request)
