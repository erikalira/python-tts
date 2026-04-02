from unittest.mock import Mock

from src.standalone.config.standalone_config import StandaloneConfig
from src.standalone.services.notification_services import (
    ConsoleNotificationService,
    NullSystemTrayIcon,
    SystemTrayService,
)


def test_console_notification_service_is_available(capsys):
    service = ConsoleNotificationService()

    service.show_info("Title", "Message")
    service.show_success("Title", "Message")
    service.show_error("Title", "Message")

    output = capsys.readouterr().out
    assert "Title: Message" in output
    assert service.is_available() is True


def test_null_system_tray_icon_is_never_available():
    tray = NullSystemTrayIcon()

    tray.show()
    tray.hide()
    tray.set_tooltip("ignored")

    assert tray.is_available() is False


def test_system_tray_service_start_returns_false_when_unavailable():
    config = StandaloneConfig.create_default()
    service = SystemTrayService(config)
    service._tray_icon = NullSystemTrayIcon()

    assert service.start() is False


def test_system_tray_service_notify_respects_configuration():
    config = StandaloneConfig.create_default()
    service = SystemTrayService(config)
    notifier = Mock()
    service._notification_service = notifier

    service.notify_info("Info", "Message")
    notifier.show_info.assert_called_once_with("Info", "Message")

    config.interface.show_notifications = False
    service.notify_error("Err", "Message")
    notifier.show_error.assert_not_called()


def test_system_tray_service_initialize_sets_handlers():
    config = StandaloneConfig.create_default()
    service = SystemTrayService(config)
    tray = Mock()
    service._tray_icon = tray

    status_click = Mock()
    configure = Mock()
    quit_handler = Mock()
    service.initialize(status_click, configure, quit_handler)

    tray.set_handlers.assert_called_once_with(status_click, configure, quit_handler)


def test_system_tray_service_get_status_reflects_runtime():
    config = StandaloneConfig.create_default()
    service = SystemTrayService(config)
    tray = Mock()
    tray.is_available.return_value = True
    service._tray_icon = tray

    status = service.get_status()

    assert status["tray_available"] is True
    assert status["notifications_enabled"] is True
