from unittest.mock import Mock

from src.application.desktop_bot import DESKTOP_BOT_TEST_MESSAGE
from src.application.tts_execution import (
    TTS_EXECUTION_RESULT_FAILED,
    TTS_EXECUTION_RESULT_MISSING_TEXT,
    TTS_EXECUTION_RESULT_OK,
)
from src.desktop.app.desktop_actions import DesktopConfigurationCoordinator
from src.desktop.app.desktop_app import DesktopApp
from src.desktop.app.tts_runtime import (
    DesktopAppHotkeyHandler,
    DesktopAppTTSResultPresenter,
)
from src.desktop.config.desktop_config import DesktopAppConfig, get_default_discord_bot_url
from src.desktop.services.hotkey_services import HotkeyEvent


def test_desktop_app_hotkey_handler_processes_captured_text():
    processor = Mock()
    presenter = Mock()
    handler = DesktopAppHotkeyHandler(processor, presenter)
    event = HotkeyEvent(text="hello", character_count=7, trigger_open="{", trigger_close="}")

    handler.handle_text_captured(event)

    presenter.show_processing.assert_called_once_with("hello")
    processor.process_text.assert_called_once()
    assert processor.process_text.call_args.args == ("hello", 7)
    assert processor.process_text.call_args.kwargs["on_complete"] == presenter.present


def test_desktop_app_hotkey_handler_ignores_empty_text():
    processor = Mock()
    presenter = Mock()
    handler = DesktopAppHotkeyHandler(processor, presenter)
    event = HotkeyEvent(text="", character_count=2, trigger_open="{", trigger_close="}")

    handler.handle_text_captured(event)

    presenter.show_processing.assert_not_called()
    processor.process_text.assert_not_called()


def test_desktop_app_tts_result_presenter_notifies_success_after_tts():
    notifier = Mock()
    presenter = DesktopAppTTSResultPresenter(notifier)

    presenter.present({"success": True, "code": TTS_EXECUTION_RESULT_OK})

    notifier.notify_success.assert_called_once_with("Desktop App", "Texto reproduzido com sucesso")


def test_desktop_app_tts_result_presenter_notifies_missing_text_error():
    notifier = Mock()
    presenter = DesktopAppTTSResultPresenter(notifier)

    presenter.present({"success": False, "code": TTS_EXECUTION_RESULT_MISSING_TEXT})

    notifier.notify_error.assert_called_once_with("Desktop App", "Nenhum texto valido foi capturado")


def test_desktop_app_tts_result_presenter_notifies_failure():
    notifier = Mock()
    presenter = DesktopAppTTSResultPresenter(notifier)

    presenter.present({"success": False, "code": TTS_EXECUTION_RESULT_FAILED})

    notifier.notify_error.assert_called_once_with("Desktop App", "Falha ao reproduzir o texto")


def test_desktop_app_tts_result_presenter_shows_processing_message():
    notifier = Mock()
    presenter = DesktopAppTTSResultPresenter(notifier)

    presenter.show_processing("hello world")

    notifier.notify_info.assert_called_once()


def test_desktop_app_handle_configure_updates_services():
    app = DesktopApp()
    app._config = DesktopAppConfig.create_default()
    app._config_service = Mock()
    updated_config = DesktopAppConfig.create_default()
    updated_config.discord.member_id = "123"
    app._config_service.get_configuration.return_value = updated_config
    app._config_repository = Mock()
    app._notification_service = Mock()
    app._update_services_config = Mock()

    app._handle_configure()

    app._config_repository.save.assert_called_once_with(updated_config)
    app._update_services_config.assert_called_once()
    app._notification_service.notify_success.assert_called_once()


def test_handle_initial_configuration_applies_updated_config_through_application_service():
    current_config = DesktopAppConfig.create_default()
    updated_config = DesktopAppConfig.create_default()
    updated_config.discord.member_id = "123"
    config_service = Mock()
    config_service.get_configuration.return_value = updated_config
    configuration_application = Mock()
    configuration_application.is_configured.return_value = False
    coordinator = DesktopConfigurationCoordinator(
        config_service=config_service,
        configuration_application=configuration_application,
    )

    should_continue, returned_config = coordinator.handle_initial_configuration(current_config)

    assert should_continue is True
    assert returned_config is updated_config
    config_service.get_configuration.assert_called_once_with(current_config)
    configuration_application.apply.assert_called_once_with(updated_config)


def test_desktop_app_handle_configure_rejects_invalid_config():
    app = DesktopApp()
    app._config = DesktopAppConfig.create_default()
    app._config_service = Mock()
    invalid_config = DesktopAppConfig.create_default()
    invalid_config.discord.member_id = "abc"
    app._config_service.get_configuration.return_value = invalid_config
    app._config_repository = Mock()
    app._notification_service = Mock()
    app._update_services_config = Mock()

    app._handle_configure()

    app._config_repository.save.assert_not_called()
    app._update_services_config.assert_not_called()
    app._notification_service.notify_error.assert_called_once()


def test_desktop_app_handle_configure_pauses_hotkeys_while_gui_is_open():
    app = DesktopApp()
    app._config = DesktopAppConfig.create_default()
    app._config_service = Mock()
    updated_config = DesktopAppConfig.create_default()
    updated_config.discord.member_id = "123"
    app._config_service.get_configuration.return_value = updated_config
    app._config_repository = Mock()
    app._notification_service = Mock()
    app._update_services_config = Mock()
    app._hotkey_manager = Mock()
    app._hotkey_manager.is_active.side_effect = [True, False]

    app._handle_configure()

    app._hotkey_manager.stop.assert_called_once()
    assert app._hotkey_manager.start.call_count == 1


def test_desktop_app_update_services_config_rebuilds_hotkey_manager():
    app = DesktopApp(
        tts_processor_factory=Mock(return_value=Mock()),
        hotkey_manager_factory=Mock(side_effect=[Mock(), Mock()]),
        notification_service_factory=Mock(side_effect=[Mock(), Mock()]),
    )
    app._config = DesktopAppConfig.create_default()
    app._tts_processor = Mock()
    app._hotkey_manager = Mock()
    app._hotkey_manager.is_active.return_value = False
    app._notification_service = Mock()
    app._notification_service.is_available.return_value = False

    app._update_services_config()

    assert app._hotkey_manager is not None
    app._hotkey_manager.initialize.assert_called_once()


def test_desktop_app_save_configuration_from_ui_applies_changes():
    app = DesktopApp()
    updated_config = DesktopAppConfig.create_default()
    updated_config.discord.bot_url = get_default_discord_bot_url()
    updated_config.discord.member_id = "123"
    app._config = DesktopAppConfig.create_default()
    app._config_repository = Mock()
    app._update_services_config = Mock()

    result = app._save_configuration_from_ui(updated_config)

    assert result["success"] is True
    app._config_repository.save.assert_called_once_with(updated_config)
    app._update_services_config.assert_called_once()


def test_desktop_app_test_bot_connection_uses_http_client(monkeypatch):
    app = DesktopApp()
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()

    fake_client = Mock()
    fake_client.has_bot_url.return_value = True
    fake_client.check_connection.return_value = {"success": True, "message": "ok"}
    monkeypatch.setattr("src.desktop.app.desktop_actions.HttpDiscordBotClient", lambda cfg: fake_client)

    result = app._test_bot_connection(config)

    assert result == {"success": True, "message": "ok"}
    fake_client.check_connection.assert_called_once_with()


def test_desktop_app_send_test_message_requires_discord_identifiers():
    app = DesktopApp()
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = None

    result = app._send_test_message(config)

    assert result["success"] is False
    assert "User ID" in result["message"]


def test_desktop_app_send_test_message_uses_http_client(monkeypatch):
    app = DesktopApp()
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = "123"

    fake_client = Mock()
    fake_client.has_bot_url.return_value = True
    fake_client.has_member_id.return_value = True
    fake_client.send_text.return_value = True
    monkeypatch.setattr("src.desktop.app.desktop_actions.HttpDiscordBotClient", lambda cfg: fake_client)

    result = app._send_test_message(config)

    assert result == {"success": True, "message": "Mensagem de teste enviada ao bot com sucesso"}
    fake_client.send_text.assert_called_once_with(DESKTOP_BOT_TEST_MESSAGE)


def test_desktop_app_send_test_message_returns_bot_error_details(monkeypatch):
    app = DesktopApp()
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = "123"

    fake_client = Mock()
    fake_client.has_bot_url.return_value = True
    fake_client.has_member_id.return_value = True
    fake_client.send_text.return_value = False
    fake_client.get_last_error_message.return_value = "Bot respondeu HTTP 400: user is not connected to a voice channel"
    monkeypatch.setattr("src.desktop.app.desktop_actions.HttpDiscordBotClient", lambda cfg: fake_client)

    result = app._send_test_message(config)

    assert result == {
        "success": False,
        "message": "Bot respondeu HTTP 400: user is not connected to a voice channel",
    }
    fake_client.send_text.assert_called_once_with(DESKTOP_BOT_TEST_MESSAGE)


def test_desktop_app_refresh_voice_context_uses_http_client(monkeypatch):
    app = DesktopApp()
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = "123"

    fake_client = Mock()
    fake_client.has_bot_url.return_value = True
    fake_client.has_member_id.return_value = True
    fake_client.fetch_voice_context.return_value = {
        "success": True,
        "message": "Canal detectado: Guild A / Sala 1",
    }
    monkeypatch.setattr("src.desktop.app.desktop_actions.HttpDiscordBotClient", lambda cfg: fake_client)

    result = app._refresh_voice_context(config)

    assert result == {
        "success": True,
        "message": "Canal detectado: Guild A / Sala 1",
    }
    fake_client.fetch_voice_context.assert_called_once_with()
