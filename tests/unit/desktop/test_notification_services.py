from unittest.mock import Mock

from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.services.notification_services import (
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
    config = DesktopAppConfig.create_default()
    service = SystemTrayService(config)
    service._tray_icon = NullSystemTrayIcon()

    assert service.start() is False


def test_system_tray_service_start_returns_true_only_after_running_confirmation():
    config = DesktopAppConfig.create_default()

    class ReadyTray:
        def __init__(self):
            self.running = False

        def is_available(self):
            return True

        def is_running(self):
            return self.running

        def show(self):
            self.running = True

        def hide(self):
            self.running = False

        def set_tooltip(self, tooltip):
            pass

    service = SystemTrayService(config, tray_icon=ReadyTray())

    assert service.start() is True
    assert service.is_running() is True


def test_system_tray_service_start_returns_false_when_tray_thread_exits_early():
    config = DesktopAppConfig.create_default()

    class FailingTray:
        def is_available(self):
            return True

        def is_running(self):
            return False

        def show(self):
            return None

        def hide(self):
            pass

        def set_tooltip(self, tooltip):
            pass

    service = SystemTrayService(config, tray_icon=FailingTray())

    assert service.start() is False
    assert service.is_running() is False


def test_system_tray_service_notify_respects_configuration():
    config = DesktopAppConfig.create_default()
    service = SystemTrayService(config)
    notifier = Mock()
    service._notification_service = notifier

    service.notify_info("Info", "Message")
    notifier.show_info.assert_called_once_with("Info", "Message")

    config.interface.show_notifications = False
    service.notify_error("Err", "Message")
    notifier.show_error.assert_not_called()


def test_system_tray_service_initialize_sets_handlers():
    config = DesktopAppConfig.create_default()
    service = SystemTrayService(config)
    tray = Mock()
    service._tray_icon = tray

    status_click = Mock()
    configure = Mock()
    quit_handler = Mock()
    service.initialize(status_click, configure, quit_handler)

    tray.set_handlers.assert_called_once_with(status_click, configure, quit_handler)


def test_system_tray_service_get_status_reflects_runtime():
    config = DesktopAppConfig.create_default()
    service = SystemTrayService(config)
    tray = Mock()
    tray.is_available.return_value = True
    tray.is_running.return_value = False
    service._tray_icon = tray

    status = service.get_status()

    assert status["tray_available"] is True
    assert status["tray_running"] is False
    assert status["notifications_enabled"] is True


def test_py_system_tray_icon_quit_without_handler_only_hides_tray():
    from src.desktop.adapters.system_tray import PySystemTrayIcon

    tray = PySystemTrayIcon(DesktopAppConfig.create_default())
    tray.hide = Mock()

    tray._handle_quit(None, None)

    tray.hide.assert_called_once_with()


def test_py_system_tray_icon_quit_with_handler_delegates_without_hiding():
    from src.desktop.adapters.system_tray import PySystemTrayIcon

    tray = PySystemTrayIcon(DesktopAppConfig.create_default())
    tray.hide = Mock()
    quit_handler = Mock()
    tray.set_handlers(quit_handler=quit_handler)

    tray._handle_quit(None, None)

    quit_handler.assert_called_once_with()
    tray.hide.assert_not_called()

