from types import SimpleNamespace

from src.standalone.config.standalone_config import StandaloneConfig
from src.standalone.gui import configuration_gui


class DummyVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value


class DummyRoot:
    def __init__(self):
        self.quit_called = False
        self.destroy_called = False
        self.mainloop_called = False
        self.title_value = None
        self.geometry_value = None
        self.resizable_args = None
        self.eval_calls = []

    def title(self, value):
        self.title_value = value

    def geometry(self, value):
        self.geometry_value = value

    def resizable(self, width, height):
        self.resizable_args = (width, height)

    def eval(self, script):
        self.eval_calls.append(script)

    def mainloop(self):
        self.mainloop_called = True

    def quit(self):
        self.quit_called = True

    def destroy(self):
        self.destroy_called = True


class DummyWidget:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.pack_calls = []
        self.bind_calls = []
        self.configure_calls = []
        self.create_window_calls = []
        self.insert_calls = []
        self.config_calls = []

    def pack(self, *args, **kwargs):
        self.pack_calls.append((args, kwargs))
        return self

    def bind(self, *args, **kwargs):
        self.bind_calls.append((args, kwargs))

    def configure(self, *args, **kwargs):
        self.configure_calls.append((args, kwargs))

    def create_window(self, *args, **kwargs):
        self.create_window_calls.append((args, kwargs))

    def bbox(self, *_args, **_kwargs):
        return (0, 0, 100, 100)

    def insert(self, *args, **kwargs):
        self.insert_calls.append((args, kwargs))

    def config(self, *args, **kwargs):
        self.config_calls.append((args, kwargs))

    def yview(self, *_args, **_kwargs):
        return None

    def set(self, *_args, **_kwargs):
        return None


def build_fake_tk_module():
    return SimpleNamespace(
        Tk=DummyRoot,
        Label=DummyWidget,
        Canvas=DummyWidget,
        Text=DummyWidget,
        StringVar=lambda value="": DummyVar(value),
        WORD="word",
    )


def build_fake_ttk_module():
    return SimpleNamespace(
        Scrollbar=DummyWidget,
        Frame=DummyWidget,
        Label=DummyWidget,
        LabelFrame=DummyWidget,
        Entry=DummyWidget,
        Combobox=DummyWidget,
        Button=DummyWidget,
    )


def test_console_configuration_interface_accepts_existing_member_id(monkeypatch):
    interface = configuration_gui.ConsoleConfigurationInterface()
    current_config = StandaloneConfig.create_default()
    current_config.discord.member_id = "123456"
    current_config.discord.guild_id = "654321"

    monkeypatch.setattr("builtins.input", lambda _prompt: "   ")

    updated = interface.show_configuration_dialog(current_config)

    assert updated.discord.member_id == "123456"
    assert updated.discord.guild_id == "654321"


def test_console_configuration_interface_retries_until_numeric(monkeypatch, capsys):
    interface = configuration_gui.ConsoleConfigurationInterface()
    current_config = StandaloneConfig.create_default()
    responses = iter(["abc", "789", "xyz", "987"])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

    updated = interface.show_configuration_dialog(current_config)

    assert updated.discord.member_id == "789"
    assert updated.discord.guild_id == "987"
    assert "deve conter apenas números" in capsys.readouterr().out.lower()


def test_gui_configuration_interface_falls_back_to_console_when_tkinter_missing(monkeypatch):
    expected = StandaloneConfig.create_default()
    expected.discord.member_id = "999"
    interface = configuration_gui.GUIConfigurationInterface()
    called = {}

    monkeypatch.setattr(configuration_gui, "_tkinter_available", False)

    def fake_console(self, current_config):
        called["current_config"] = current_config
        return expected

    monkeypatch.setattr(
        configuration_gui.ConsoleConfigurationInterface,
        "show_configuration_dialog",
        fake_console,
    )

    result = interface.show_configuration_dialog(StandaloneConfig.create_default())

    assert result is expected
    assert isinstance(called["current_config"], StandaloneConfig)


def test_gui_configuration_interface_falls_back_to_console_on_exception(monkeypatch):
    expected = StandaloneConfig.create_default()
    expected.discord.member_id = "321"
    interface = configuration_gui.GUIConfigurationInterface()

    monkeypatch.setattr(configuration_gui, "_tkinter_available", True)
    monkeypatch.setattr(interface, "_create_window", lambda: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(
        configuration_gui.ConsoleConfigurationInterface,
        "show_configuration_dialog",
        lambda self, current_config: expected,
    )

    result = interface.show_configuration_dialog(StandaloneConfig.create_default())

    assert result is expected


def test_gui_create_window_configures_root(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    monkeypatch.setattr(configuration_gui, "tk", build_fake_tk_module())

    interface._create_window()

    assert interface.root.title_value == "TTS Hotkey - Configuração"
    assert interface.root.geometry_value == "500x500"
    assert interface.root.resizable_args == (False, False)
    assert interface.root.eval_calls == ["tk::PlaceWindow . center"]


def test_gui_create_widgets_builds_form_variables(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    interface.root = DummyRoot()
    interface._current_config = StandaloneConfig.create_default()
    interface._current_config.discord.member_id = "123"
    interface._current_config.discord.guild_id = "456"
    interface._current_config.discord.bot_url = "http://bot"
    interface._current_config.tts.engine = "edge-tts"
    interface._current_config.tts.language = "en"

    monkeypatch.setattr(configuration_gui, "tk", build_fake_tk_module())
    monkeypatch.setattr(configuration_gui, "ttk", build_fake_ttk_module())

    interface._create_widgets()

    assert interface.member_id_var.get() == "123"
    assert interface.guild_id_var.get() == "456"
    assert interface.bot_url_var.get() == "http://bot"
    assert interface.engine_var.get() == "edge-tts"
    assert interface.language_var.get() == "en"


def test_gui_save_config_requires_member_id(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    interface._current_config = StandaloneConfig.create_default()
    interface.member_id_var = DummyVar("   ")
    interface.guild_id_var = DummyVar("456")
    interface.bot_url_var = DummyVar("http://bot")
    interface.engine_var = DummyVar("gtts")
    interface.language_var = DummyVar("pt")
    errors = []

    monkeypatch.setattr(configuration_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    interface._save_config()

    assert interface.result is None
    assert errors == [("Erro", "Discord User ID é obrigatório!")]


def test_gui_save_config_requires_numeric_member_id(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    interface._current_config = StandaloneConfig.create_default()
    interface.member_id_var = DummyVar("abc")
    interface.guild_id_var = DummyVar("456")
    interface.bot_url_var = DummyVar("http://bot")
    interface.engine_var = DummyVar("gtts")
    interface.language_var = DummyVar("pt")
    errors = []

    monkeypatch.setattr(configuration_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    interface._save_config()

    assert interface.result is None
    assert errors == [("Erro", "Discord User ID deve conter apenas números!")]


def test_gui_save_config_requires_guild_id(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    interface._current_config = StandaloneConfig.create_default()
    interface.member_id_var = DummyVar("123")
    interface.guild_id_var = DummyVar("   ")
    interface.bot_url_var = DummyVar("http://bot")
    interface.engine_var = DummyVar("gtts")
    interface.language_var = DummyVar("pt")
    errors = []

    monkeypatch.setattr(configuration_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    interface._save_config()

    assert interface.result is None
    assert errors == [("Erro", "Discord Guild ID é obrigatório!")]


def test_gui_save_config_requires_numeric_guild_id(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    interface._current_config = StandaloneConfig.create_default()
    interface.member_id_var = DummyVar("123")
    interface.guild_id_var = DummyVar("abc")
    interface.bot_url_var = DummyVar("http://bot")
    interface.engine_var = DummyVar("gtts")
    interface.language_var = DummyVar("pt")
    errors = []

    monkeypatch.setattr(configuration_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    interface._save_config()

    assert interface.result is None
    assert errors == [("Erro", "Discord Guild ID deve conter apenas números!")]


def test_gui_save_config_reports_validation_errors(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    interface._current_config = StandaloneConfig.create_default()
    interface.member_id_var = DummyVar("123")
    interface.guild_id_var = DummyVar("456")
    interface.bot_url_var = DummyVar("http://bot")
    interface.engine_var = DummyVar("gtts")
    interface.language_var = DummyVar("pt")
    errors = []

    monkeypatch.setattr(
        configuration_gui.ConfigurationValidator,
        "validate",
        lambda config: (False, ["invalid timeout", "invalid rate"]),
    )
    monkeypatch.setattr(configuration_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    interface._save_config()

    assert interface.result is None
    assert errors == [("Erro de Validação", "invalid timeout\ninvalid rate")]


def test_gui_save_config_updates_result_and_closes_window(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    current_config = StandaloneConfig.create_default()
    current_config.discord.bot_url = "http://old-bot"
    interface._current_config = current_config
    interface.member_id_var = DummyVar("123")
    interface.guild_id_var = DummyVar("456")
    interface.bot_url_var = DummyVar("http://new-bot")
    interface.engine_var = DummyVar("pyttsx3")
    interface.language_var = DummyVar("en")
    closed = []

    monkeypatch.setattr(configuration_gui.ConfigurationValidator, "validate", lambda config: (True, []))
    monkeypatch.setattr(interface, "_close_window", lambda: closed.append(True))

    interface._save_config()

    assert interface.result is not None
    assert interface.result.discord.member_id == "123"
    assert interface.result.discord.guild_id == "456"
    assert interface.result.discord.bot_url == "http://new-bot"
    assert interface.result.tts.engine == "pyttsx3"
    assert interface.result.tts.language == "en"
    assert closed == [True]


def test_gui_save_config_preserves_existing_bot_url_when_blank(monkeypatch):
    interface = configuration_gui.GUIConfigurationInterface()
    current_config = StandaloneConfig.create_default()
    current_config.discord.bot_url = "http://existing-bot"
    current_config.discord.guild_id = "999"
    interface._current_config = current_config
    interface.member_id_var = DummyVar("123")
    interface.guild_id_var = DummyVar("999")
    interface.bot_url_var = DummyVar("   ")
    interface.engine_var = DummyVar("gtts")
    interface.language_var = DummyVar("pt")

    monkeypatch.setattr(configuration_gui.ConfigurationValidator, "validate", lambda config: (True, []))
    monkeypatch.setattr(interface, "_close_window", lambda: None)

    interface._save_config()

    assert interface.result.discord.bot_url == "http://existing-bot"


def test_gui_cancel_and_close_window():
    interface = configuration_gui.GUIConfigurationInterface()
    interface.root = DummyRoot()
    interface.result = StandaloneConfig.create_default()

    interface._cancel()

    assert interface.result is None
    assert interface.root.quit_called is True
    assert interface.root.destroy_called is True


def test_configuration_ui_factory_respects_preference(monkeypatch):
    monkeypatch.setattr(configuration_gui, "_tkinter_available", True)
    assert isinstance(configuration_gui.ConfigurationUIFactory.create_interface(), configuration_gui.GUIConfigurationInterface)
    assert isinstance(configuration_gui.ConfigurationUIFactory.create_interface(prefer_gui=False), configuration_gui.ConsoleConfigurationInterface)


def test_configuration_display_service_shows_local_mode_without_optional_dependencies(monkeypatch, capsys):
    service = configuration_gui.ConfigurationDisplayService()
    config = StandaloneConfig.create_default()
    config.discord.bot_url = ""
    config.discord.member_id = None
    config.discord.guild_id = None

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name in {"requests", "pystray"}:
            raise ImportError(name)
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    service.show_current_configuration(config)

    output = capsys.readouterr().out
    assert "MODO LOCAL" in output.upper()
    assert "REQUESTS" in output.upper()
    assert "SYSTEM TRAY: ❌" in output.upper()


def test_configuration_display_service_shows_discord_mode_when_requests_is_available(monkeypatch, capsys):
    service = configuration_gui.ConfigurationDisplayService()
    config = StandaloneConfig.create_default()
    config.discord.bot_url = "http://localhost:10000"
    config.discord.member_id = "123"
    config.discord.guild_id = "456"

    original_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == "requests":
            return SimpleNamespace()
        if name == "pystray":
            return SimpleNamespace()
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr("builtins.__import__", fake_import)

    service.show_current_configuration(config)

    output = capsys.readouterr().out
    assert "MODO DISCORD" in output.upper()
    assert "SYSTEM TRAY: ✅" in output.upper()
