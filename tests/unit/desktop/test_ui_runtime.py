from unittest.mock import Mock

from src.application.dto import DesktopAppRuntimeStatusDTO
from src.desktop.app.ui_runtime import DesktopAppUIRuntimeCoordinator
from src.desktop.config.desktop_config import DesktopAppConfig


def test_ui_runtime_coordinator_shows_main_window(monkeypatch):
    created_window = Mock()
    window_factory = Mock(return_value=created_window)
    monkeypatch.setattr("src.desktop.app.ui_runtime.DesktopAppMainWindow", window_factory)
    coordinator = DesktopAppUIRuntimeCoordinator()
    config = DesktopAppConfig.create_default()

    coordinator.show_main_window(
        config=config,
        on_save=Mock(),
        on_test_connection=Mock(),
        on_send_test=Mock(),
        on_refresh_voice_context=Mock(),
    )

    assert coordinator.main_window is created_window
    created_window.show.assert_called_once_with()
    assert window_factory.call_args.args[0] is config


def test_ui_runtime_coordinator_queues_actions():
    coordinator = DesktopAppUIRuntimeCoordinator()
    action = Mock()

    coordinator.queue(action)

    queued_action = coordinator.action_queue.get_nowait()
    assert queued_action is action


def test_ui_runtime_coordinator_drains_queued_actions():
    coordinator = DesktopAppUIRuntimeCoordinator()
    action_one = Mock()
    action_two = Mock()
    coordinator.queue(action_one)
    coordinator.queue(action_two)

    coordinator.drain_queued_actions()

    action_one.assert_called_once_with()
    action_two.assert_called_once_with()
    assert coordinator.action_queue.empty()


def test_ui_runtime_coordinator_show_status_focuses_existing_window():
    coordinator = DesktopAppUIRuntimeCoordinator()
    coordinator._main_window = Mock()

    coordinator.show_status(
        get_status=Mock(),
        notification_service=Mock(),
    )

    coordinator.main_window.focus.assert_called_once_with()
    coordinator.main_window.push_log.assert_called_once_with("Main window brought to front from tray")


def test_ui_runtime_coordinator_show_status_notifies_when_window_is_closed():
    coordinator = DesktopAppUIRuntimeCoordinator()
    notification_service = Mock()

    coordinator.show_status(
        get_status=lambda: DesktopAppRuntimeStatusDTO(
            initialized=True,
            running=True,
            discord_configured=True,
            hotkey_active=False,
            tts_available=True,
            tray_available=True,
        ),
        notification_service=notification_service,
    )

    notification_service.notify_info.assert_called_once_with(
        "Desktop App",
        "Discord mode | Hotkeys inactive | TTS available",
    )


def test_ui_runtime_coordinator_handle_configure_focuses_existing_window():
    coordinator = DesktopAppUIRuntimeCoordinator()
    coordinator._main_window = Mock()

    updated_config, applied = coordinator.handle_configure(
        ensure_action_coordinators=Mock(),
        hotkey_manager=Mock(),
        get_configuration_coordinator=Mock(),
        current_config=Mock(),
        notification_service=Mock(),
    )

    assert (updated_config, applied) == (None, False)
    coordinator.main_window.focus.assert_called_once_with()
    coordinator.main_window.push_log.assert_called_once_with("Configuration action requested from tray")


# pyright: reportAttributeAccessIssue=false, reportOptionalMemberAccess=false
