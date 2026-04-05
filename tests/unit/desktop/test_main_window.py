from types import SimpleNamespace
from unittest.mock import Mock

from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.gui.main_window import DesktopAppMainWindow
from src.desktop.gui.main_window_presenter import ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR


class DummyVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class DummyLabel:
    def __init__(self):
        self.fg = None

    def configure(self, **kwargs):
        if "fg" in kwargs:
            self.fg = kwargs["fg"]


class DummyTextWidget:
    def __init__(self):
        self.configure_calls = []
        self.delete_calls = []
        self.insert_calls = []
        self.see_calls = []

    def configure(self, **kwargs):
        self.configure_calls.append(kwargs)

    def delete(self, start, end):
        self.delete_calls.append((start, end))

    def insert(self, end, text):
        self.insert_calls.append((end, text))

    def see(self, end):
        self.see_calls.append(end)


class DummyRoot:
    def __init__(self):
        self.after_calls = []
        self.withdraw_calls = 0

    def after(self, delay_ms, callback):
        self.after_calls.append((delay_ms, callback))

    def withdraw(self):
        self.withdraw_calls += 1


def build_main_window():
    return DesktopAppMainWindow(
        config=DesktopAppConfig.create_default(),
        on_save=Mock(),
        on_test_connection=Mock(),
        on_send_test=Mock(),
        on_refresh_voice_context=Mock(),
    )


def test_main_window_handle_test_connection_uses_presenter_feedback():
    window = build_main_window()
    config = DesktopAppConfig.create_default()
    window._build_config_from_form = Mock(return_value=config)
    window._on_test_connection = Mock(return_value={"success": True, "message": "Bot online"})
    window._connection_var = DummyVar()
    window._connection_label = DummyLabel()

    window._handle_test_connection()

    assert window._connection_var.get() == "Bot online"
    assert window._connection_label.fg == SUCCESS_COLOR


def test_main_window_handle_send_test_reports_invalid_value():
    window = build_main_window()
    window._build_config_from_form = Mock(side_effect=ValueError("porta"))
    window._connection_var = DummyVar()
    window._connection_label = DummyLabel()

    window._handle_send_test()

    assert window._connection_var.get() == "Envio de teste falhou: valor invalido (porta)"
    assert window._connection_label.fg == ERROR_COLOR


def test_main_window_handle_refresh_voice_context_updates_voice_context_message():
    window = build_main_window()
    config = DesktopAppConfig.create_default()
    window._build_config_from_form = Mock(return_value=config)
    window._on_refresh_voice_context = Mock(return_value={"success": False, "message": "Usuario fora do canal"})
    window._voice_context_var = DummyVar()
    window._voice_context_label = DummyLabel()

    window._handle_refresh_voice_context()

    assert window._voice_context_var.get() == "Usuario fora do canal"
    assert window._voice_context_label.fg == ERROR_COLOR


def test_main_window_refresh_local_status_uses_presenter_summary():
    window = build_main_window()
    window._config_var = DummyVar()
    window._config_label = DummyLabel()

    window._refresh_local_status()

    assert "Configuracao incompleta" in window._config_var.get()
    assert window._config_label.fg == WARNING_COLOR


def test_main_window_set_status_updates_status_var_and_color():
    window = build_main_window()
    window._status_var = DummyVar()
    window._status_label = DummyLabel()
    window.push_log = Mock()

    window._set_status("Tudo certo", success=True)

    assert window._status_var.get() == "OK: Tudo certo"
    assert window._status_label.fg == SUCCESS_COLOR
    window.push_log.assert_called_once_with("Tudo certo")


def test_main_window_clear_logs_resets_widget_and_pushes_log(monkeypatch):
    window = build_main_window()
    window._logs_widget = DummyTextWidget()
    window.push_log = Mock()
    monkeypatch.setattr(
        "src.desktop.gui.tk_support.tk",
        SimpleNamespace(END="end"),
    )

    window._clear_logs()

    assert window._logs_widget.configure_calls == [{"state": "normal"}, {"state": "disabled"}]
    assert window._logs_widget.delete_calls == [("1.0", "end")]
    window.push_log.assert_called_once_with("Logs limpos pelo usuario")


def test_main_window_drain_logs_appends_messages_and_reschedules():
    window = build_main_window()
    window.root = DummyRoot()
    window._append_log = Mock()
    window.push_log("linha 1")
    window.push_log("linha 2")

    window._drain_logs()

    assert window._append_log.call_count == 2
    assert [call.args[0] for call in window._append_log.call_args_list] == ["linha 1", "linha 2"]
    assert window.root.after_calls == [(250, window._drain_logs)]


def test_main_window_hide_to_tray_withdraws_root_and_logs_action():
    window = build_main_window()
    window.root = DummyRoot()

    window.hide_to_tray()

    assert window.root.withdraw_calls == 1
    assert window._log_queue.get_nowait() == "Janela principal minimizada para a bandeja"


def test_main_window_drain_ui_actions_runs_callback_and_reschedules():
    callback = Mock()
    window = DesktopAppMainWindow(
        config=DesktopAppConfig.create_default(),
        on_save=Mock(),
        on_test_connection=Mock(),
        on_send_test=Mock(),
        on_refresh_voice_context=Mock(),
        on_process_ui_actions=callback,
    )
    window.root = DummyRoot()

    window._drain_ui_actions()

    callback.assert_called_once_with()
    assert window.root.after_calls == [(100, window._drain_ui_actions)]
