from unittest.mock import Mock

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
