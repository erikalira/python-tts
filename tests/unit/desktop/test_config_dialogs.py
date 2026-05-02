import logging
from types import SimpleNamespace

import pytest

from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.gui import tk_support
from src.desktop.gui.config_dialog_presenter import ConfigDialogsPresenter, InitialSetupResult
from src.desktop.gui.config_dialogs import ConsoleConfig, GUIConfig, InitialSetupGUI
from src.desktop.gui.ui_logging import UILogHandler


class DummyVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value

    def set(self, value):
        self._value = value


class DummyRoot:
    def __init__(self):
        self.destroy_called = False
        self.mainloop_called = False
        self.title_value = None
        self.geometry_calls = []
        self.resizable_args = None
        self.transient_called = False
        self.grab_set_called = False
        self.update_idletasks_called = False
        self.protocol_calls = []
        self.after_calls = []

    def title(self, value):
        self.title_value = value

    def geometry(self, value):
        self.geometry_calls.append(value)

    def resizable(self, width, height):
        self.resizable_args = (width, height)

    def transient(self):
        self.transient_called = True

    def grab_set(self):
        self.grab_set_called = True

    def mainloop(self):
        self.mainloop_called = True

    def destroy(self):
        self.destroy_called = True

    def protocol(self, name, callback):
        self.protocol_calls.append((name, callback))

    def after(self, delay_ms, callback):
        self.after_calls.append((delay_ms, callback))

    def winfo_screenwidth(self):
        return 1200

    def winfo_screenheight(self):
        return 800

    def update_idletasks(self):
        self.update_idletasks_called = True

    def winfo_width(self):
        return 600

    def winfo_height(self):
        return 500


class DummyWidget:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pack_calls = []

    def pack(self, *args, **kwargs):
        self.pack_calls.append((args, kwargs))
        return self

    def add(self, *_args, **_kwargs):
        return None


def build_fake_tk_module():
    return SimpleNamespace(
        Tk=DummyRoot,
        StringVar=lambda value="": DummyVar(value),
        BooleanVar=lambda value=False: DummyVar(value),
        BOTH="both",
        CENTER="center",
        X="x",
        W="w",
        LEFT="left",
        RIGHT="right",
        END="end",
    )


def build_fake_ttk_module():
    return SimpleNamespace(
        Frame=DummyWidget,
        Label=DummyWidget,
        LabelFrame=DummyWidget,
        Entry=DummyWidget,
        Button=DummyWidget,
        Checkbutton=DummyWidget,
        Scrollbar=DummyWidget,
        Combobox=DummyWidget,
        Notebook=DummyWidget,
    )


@pytest.fixture(autouse=True)
def prevent_real_messageboxes(monkeypatch):
    calls = {"info": [], "error": []}
    monkeypatch.setattr(
        tk_support,
        "messagebox",
        SimpleNamespace(
            showinfo=lambda title, message: calls["info"].append((title, message)),
            showerror=lambda title, message: calls["error"].append((title, message)),
        ),
    )
    return calls


def test_console_config_keeps_existing_values_when_inputs_are_blank(monkeypatch):
    config = DesktopAppConfig.create_default()
    config.discord.member_id = "123"
    config.discord.bot_url = "http://bot"
    config.tts.engine = "gtts"
    config.tts.language = "pt"
    config.tts.voice_id = "voice"
    config.tts.rate = 180
    responses = iter(["", "", "", "", "", "", "", "", "", ""])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

    result = ConsoleConfig().show_config(config)

    assert result is not None
    assert result.discord.member_id == "123"
    assert result.discord.bot_url == "http://bot"
    assert result.tts.engine == "gtts"
    assert result.tts.rate == 180
    assert result.interface.local_tts_enabled is False


def test_initial_setup_gui_create_widgets_populates_variables(monkeypatch):
    gui = InitialSetupGUI()
    gui.root = DummyRoot()

    monkeypatch.setenv("DISCORD_BOT_URL", "http://env-bot")
    monkeypatch.setattr(tk_support, "tk", build_fake_tk_module())
    monkeypatch.setattr(tk_support, "ttk", build_fake_ttk_module())

    gui._create_initial_setup_widgets()

    assert gui.member_id_var.get() == ""
    assert gui.bot_url_var.get() == "http://env-bot"


def test_initial_setup_gui_skip_discord_sets_result_and_destroys_root(monkeypatch):
    gui = InitialSetupGUI()
    gui.root = DummyRoot()

    monkeypatch.setenv("DISCORD_BOT_URL", "http://bot")

    gui._skip_discord()

    assert gui.result == InitialSetupResult(
        member_id=None,
        bot_url="http://bot",
        skip_discord=True,
    )
    assert gui.root.destroy_called is True


def test_initial_setup_gui_save_and_continue_validates_member_id(prevent_real_messageboxes):
    gui = InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("abc")
    gui.bot_url_var = DummyVar("http://bot")

    gui._save_and_continue()

    assert gui.result is None
    assert prevent_real_messageboxes["error"] == [("Error", "Discord User ID must contain only numbers!")]


def test_initial_setup_gui_save_and_continue_requires_bot_url(prevent_real_messageboxes):
    gui = InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("123")
    gui.bot_url_var = DummyVar("   ")

    gui._save_and_continue()

    assert gui.result is None
    assert prevent_real_messageboxes["error"] == [("Error", "Bot URL is required!")]


def test_initial_setup_gui_save_and_continue_with_member_id(prevent_real_messageboxes):
    gui = InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("123")
    gui.bot_url_var = DummyVar("http://bot")

    gui._save_and_continue()

    assert gui.result == InitialSetupResult(
        member_id="123",
        bot_url="http://bot",
        skip_discord=False,
    )
    assert prevent_real_messageboxes["info"] == [("Success", "Configuration saved! TTS will work on Discord.")]
    assert gui.root.destroy_called is True


def test_initial_setup_gui_save_and_continue_without_member_id(prevent_real_messageboxes):
    gui = InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("   ")
    gui.bot_url_var = DummyVar("http://bot")

    gui._save_and_continue()

    assert gui.result == InitialSetupResult(
        member_id=None,
        bot_url="http://bot",
        skip_discord=False,
    )
    assert prevent_real_messageboxes["info"] == [("Aviso", "Sem Discord User ID, o TTS funcionara apenas localmente.")]


def test_console_initial_setup_handles_invalid_ids_and_defaults(monkeypatch, capsys):
    gui = InitialSetupGUI()
    responses = iter(["abc", ""])

    monkeypatch.setenv("DISCORD_BOT_URL", "http://default-bot")
    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

    result = gui._console_initial_setup()

    assert result == InitialSetupResult(
        member_id=None,
        bot_url="http://default-bot",
        skip_discord=True,
    )
    output = capsys.readouterr().out
    assert "id must contain only numbers" in output.lower()


def test_gui_config_show_config_creates_window_and_returns_result(monkeypatch):
    gui = GUIConfig()
    config = DesktopAppConfig.create_default()

    monkeypatch.setattr(tk_support, "TKINTER_AVAILABLE", True)
    monkeypatch.setattr(tk_support, "tk", build_fake_tk_module())
    monkeypatch.setattr(gui, "_create_interface", lambda: setattr(gui, "result", config))

    result = gui.show_config(config)

    assert result is config
    assert gui.root.title_value == "Desktop App - Configuration"
    assert gui.root.resizable_args == (True, True)
    assert gui.root.protocol_calls
    assert gui.root.update_idletasks_called is True
    assert gui.root.mainloop_called is True


def test_gui_config_create_tabs_populates_variables(monkeypatch):
    from tests.conftest import MockTTSCatalog

    gui = GUIConfig(tts_catalog=MockTTSCatalog())
    gui.root = DummyRoot()
    gui.config = DesktopAppConfig.create_default()
    gui.config.discord.member_id = "123"
    gui.config.discord.bot_url = "http://bot"
    gui.config.tts.engine = "pyttsx3"
    gui.config.tts.language = "system"
    gui.config.tts.voice_id = "David"
    gui.config.tts.rate = 220
    gui.config.hotkey.trigger_open = "["
    gui.config.hotkey.trigger_close = "]"
    gui.config.interface.local_tts_enabled = True

    monkeypatch.setattr(tk_support, "tk", build_fake_tk_module())
    monkeypatch.setattr(tk_support, "ttk", build_fake_ttk_module())

    gui._create_interface()

    assert gui.member_id_var.get() == "123"
    assert gui.bot_url_var.get() == "http://bot"
    assert gui.engine_var.get() == "pyttsx3"
    assert gui.voice_selection_var.get() == "R.E.P.O. - Microsoft David"
    assert gui.language_var.get() == "system"
    assert gui.voice_id_var.get() == "David"
    assert gui.rate_var.get() == "220"
    assert gui.trigger_open_var.get() == "["
    assert gui.trigger_close_var.get() == "]"
    assert gui.show_notifications_var.get() is True
    assert gui.console_logs_var.get() is True
    assert gui.local_tts_enabled_var.get() is True


def test_gui_config_save_config_saves_valid_configuration(monkeypatch):
    from src.desktop.gui import settings_gui_dialog

    gui = GUIConfig()
    gui.root = DummyRoot()
    gui.config = DesktopAppConfig.create_default()
    gui.member_id_var = DummyVar("123")
    gui.bot_url_var = DummyVar("http://bot")
    gui.engine_var = DummyVar("pyttsx3")
    gui.voice_selection_var = DummyVar("")
    gui.language_var = DummyVar("en")
    gui.voice_id_var = DummyVar("voice")
    gui.rate_var = DummyVar("210")
    gui.trigger_open_var = DummyVar("[")
    gui.trigger_close_var = DummyVar("]")
    gui.show_notifications_var = DummyVar(True)
    gui.console_logs_var = DummyVar(True)
    gui.local_tts_enabled_var = DummyVar(True)

    monkeypatch.setattr(settings_gui_dialog.ConfigurationValidator, "validate", lambda config: (True, []))

    gui._save_config()

    assert gui.result is not None
    assert gui.result.discord.member_id == "123"
    assert gui.result.tts.engine == "pyttsx3"
    assert gui.result.tts.rate == 210
    assert gui.result.interface.local_tts_enabled is True
    assert gui.result.hotkey.trigger_open == "["
    assert gui.root.destroy_called is True


def test_gui_config_save_config_shows_validation_errors(monkeypatch, prevent_real_messageboxes):
    from src.desktop.gui import settings_gui_dialog

    gui = GUIConfig()
    gui.config = DesktopAppConfig.create_default()
    gui.member_id_var = DummyVar("123")
    gui.bot_url_var = DummyVar("http://bot")
    gui.engine_var = DummyVar("gtts")
    gui.voice_selection_var = DummyVar("")
    gui.language_var = DummyVar("pt")
    gui.voice_id_var = DummyVar("voice")
    gui.rate_var = DummyVar("180")
    gui.trigger_open_var = DummyVar("{")
    gui.trigger_close_var = DummyVar("}")
    gui.show_notifications_var = DummyVar(True)
    gui.console_logs_var = DummyVar(True)
    gui.local_tts_enabled_var = DummyVar(False)

    monkeypatch.setattr(settings_gui_dialog.ConfigurationValidator, "validate", lambda config: (False, ["bad rate"]))

    gui._save_config()

    assert gui.result is None
    assert prevent_real_messageboxes["error"] == [("Validation Error", "Errors found:\n\nbad rate")]


def test_gui_config_handle_voice_selection_updates_fields():
    from tests.conftest import MockTTSCatalog

    gui = GUIConfig(tts_catalog=MockTTSCatalog())
    gui.voice_selection_var = DummyVar("Edge TTS - Francisca (PT-BR Neural)")
    gui.engine_var = DummyVar("gtts")
    gui.language_var = DummyVar("pt")
    gui.voice_id_var = DummyVar("roa/pt-br")
    gui._list_voice_labels()

    gui._handle_voice_selection()

    assert gui.engine_var.get() == "edge-tts"
    assert gui.language_var.get() == "pt-BR"
    assert gui.voice_id_var.get() == "pt-BR-FranciscaNeural"


def test_config_dialogs_presenter_builds_initial_setup_result():
    presenter = ConfigDialogsPresenter()

    result, feedback = presenter.build_initial_setup_result(
        member_id="123",
        bot_url="http://bot",
    )

    assert result == InitialSetupResult(
        member_id="123",
        bot_url="http://bot",
        skip_discord=False,
    )
    assert feedback.title == "Success"
    assert "Discord" in feedback.message


def test_config_dialogs_presenter_validates_initial_setup():
    presenter = ConfigDialogsPresenter()

    error = presenter.validate_initial_setup(
        member_id="abc",
        bot_url="http://bot",
    )

    assert error is not None
    assert error.title == "Error"
    assert "numbers" in error.message


def test_ui_log_handler_reports_queue_errors(monkeypatch):
    class FailingQueue:
        def put_nowait(self, _message):
            raise RuntimeError("queue full")

    handler = UILogHandler(FailingQueue())
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    reported = []
    monkeypatch.setattr(handler, "handleError", lambda error_record: reported.append(error_record))

    handler.emit(record)

    assert reported == [record]


# pyright: reportArgumentType=false, reportOptionalMemberAccess=false
