from queue import Queue
from threading import Event
from unittest.mock import Mock

from src.desktop.app.runtime_lifecycle import DesktopAppLifecycleCoordinator


def test_runtime_lifecycle_start_services_starts_hotkeys_and_tray():
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=False)
    hotkey_manager = Mock()
    hotkey_manager.start.return_value = True
    notification_service = Mock()
    notification_service.start.return_value = True

    result = coordinator.start_services(hotkey_manager, notification_service)

    assert result is True
    hotkey_manager.start.assert_called_once_with()
    notification_service.start.assert_called_once_with()


def test_runtime_lifecycle_start_services_fails_when_hotkeys_do_not_start():
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=False)
    hotkey_manager = Mock()
    hotkey_manager.start.return_value = False
    notification_service = Mock()

    result = coordinator.start_services(hotkey_manager, notification_service)

    assert result is False
    notification_service.start.assert_not_called()


def test_runtime_lifecycle_run_main_loop_shows_main_window_when_tkinter_is_available():
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=True)
    show_main_window = Mock()

    coordinator.run_main_loop(
        show_main_window=show_main_window,
        notification_service=Mock(),
        process_pending_ui_action=Mock(),
        is_running=lambda: False,
        shutdown_requested=Event(),
        console_wait_factory=Mock(),
    )

    show_main_window.assert_called_once_with()


def test_runtime_lifecycle_run_main_loop_processes_ui_actions_while_tray_is_running():
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=False)
    notification_service = Mock()
    notification_service.is_running.return_value = True
    process_pending_ui_action = Mock()
    shutdown_requested = Event()
    state = {"calls": 0}

    def is_running():
        state["calls"] += 1
        return state["calls"] == 1

    coordinator.run_main_loop(
        show_main_window=Mock(),
        notification_service=notification_service,
        process_pending_ui_action=process_pending_ui_action,
        is_running=is_running,
        shutdown_requested=shutdown_requested,
        console_wait_factory=Mock(),
    )

    process_pending_ui_action.assert_called_once_with(0.2)


def test_runtime_lifecycle_run_main_loop_uses_console_wait_backend_when_available(monkeypatch):
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=False)
    notification_service = Mock()
    notification_service.is_running.return_value = False
    wait_backend = Mock()
    wait_backend.is_available.return_value = True
    keyboard_module = Mock()
    monkeypatch.setitem(__import__("sys").modules, "keyboard", keyboard_module)

    coordinator.run_main_loop(
        show_main_window=Mock(),
        notification_service=notification_service,
        process_pending_ui_action=Mock(),
        is_running=lambda: False,
        shutdown_requested=Event(),
        console_wait_factory=lambda: wait_backend,
    )

    keyboard_module.wait.assert_called_once_with()


def test_runtime_lifecycle_run_main_loop_falls_back_to_input_when_console_backend_is_unavailable(monkeypatch):
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=False)
    notification_service = Mock()
    notification_service.is_running.return_value = False
    wait_backend = Mock()
    wait_backend.is_available.return_value = False
    input_mock = Mock(return_value="")
    monkeypatch.setattr("builtins.input", input_mock)

    coordinator.run_main_loop(
        show_main_window=Mock(),
        notification_service=notification_service,
        process_pending_ui_action=Mock(),
        is_running=lambda: False,
        shutdown_requested=Event(),
        console_wait_factory=lambda: wait_backend,
    )

    input_mock.assert_called_once_with("Pressione Enter para sair...")


def test_runtime_lifecycle_update_services_config_restarts_dependencies_when_needed():
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=False)
    config = object()
    hotkey_manager = Mock()
    hotkey_manager.is_active.return_value = True
    tts_processor = object()
    notification_service = Mock()
    notification_service.is_available.return_value = True
    new_tts_processor = object()
    new_notification_service = Mock()
    initialize_notification_service = Mock()
    rebuild_hotkey_manager = Mock()

    updated_tts, updated_notification = coordinator.update_services_config(
        running=True,
        config=config,
        hotkey_manager=hotkey_manager,
        tts_processor=tts_processor,
        notification_service=notification_service,
        tts_processor_factory=lambda cfg: new_tts_processor,
        notification_service_factory=lambda cfg: new_notification_service,
        initialize_notification_service=initialize_notification_service,
        rebuild_hotkey_manager=rebuild_hotkey_manager,
    )

    assert updated_tts is new_tts_processor
    assert updated_notification is new_notification_service
    hotkey_manager.stop.assert_called_once_with()
    notification_service.stop.assert_called_once_with()
    initialize_notification_service.assert_called_once_with(new_notification_service)
    new_notification_service.start.assert_called_once_with()
    rebuild_hotkey_manager.assert_called_once_with(True)


def test_runtime_lifecycle_shutdown_stops_services_and_quits_window():
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=False)
    hotkey_manager = Mock()
    notification_service = Mock()
    shutdown_requested = Event()
    root = Mock()
    main_window = Mock()
    main_window.root = root

    running = coordinator.shutdown(
        running=True,
        hotkey_manager=hotkey_manager,
        notification_service=notification_service,
        shutdown_requested=shutdown_requested,
        main_window=main_window,
    )

    assert running is False
    assert shutdown_requested.is_set() is True
    hotkey_manager.stop.assert_called_once_with()
    notification_service.stop.assert_called_once_with()
    root.quit.assert_called_once_with()


def test_runtime_lifecycle_process_pending_ui_action_runs_next_action():
    coordinator = DesktopAppLifecycleCoordinator(tkinter_available=False)
    action = Mock()
    action_queue = Queue()
    action_queue.put(action)

    coordinator.process_pending_ui_action(action_queue=action_queue, timeout=0.1)

    action.assert_called_once_with()
