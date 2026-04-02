from types import SimpleNamespace

from src.standalone.config.standalone_config import StandaloneConfig
from src.standalone.gui import simple_gui


class DummyVar:
    def __init__(self, value=""):
        self._value = value

    def get(self):
        return self._value


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
        BOTH="both",
        CENTER="center",
        X="x",
        W="w",
        LEFT="left",
        RIGHT="right",
    )


def build_fake_ttk_module():
    return SimpleNamespace(
        Frame=DummyWidget,
        Label=DummyWidget,
        LabelFrame=DummyWidget,
        Entry=DummyWidget,
        Button=DummyWidget,
        Combobox=DummyWidget,
        Notebook=DummyWidget,
    )


def test_console_config_keeps_existing_values_when_inputs_are_blank(monkeypatch):
    config = StandaloneConfig.create_default()
    config.discord.member_id = "123"
    config.discord.guild_id = "456"
    config.discord.bot_url = "http://bot"
    config.tts.engine = "gtts"
    config.tts.language = "pt"
    config.tts.voice_id = "voice"
    config.tts.rate = 180
    responses = iter(["", "", "", "", "", "", "", "", ""])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

    result = simple_gui.ConsoleConfig().show_config(config)

    assert result is not None
    assert result.discord.member_id == "123"
    assert result.discord.guild_id == "456"
    assert result.discord.bot_url == "http://bot"
    assert result.tts.engine == "gtts"
    assert result.tts.rate == 180


def test_console_config_retries_invalid_choices_and_returns_none_on_validation_error(monkeypatch, capsys):
    config = StandaloneConfig.create_default()
    responses = iter([
        "abc",
        "123",
        "xyz",
        "789",
        "",
        "3",
        "2",
        "",
        "",
        "abc",
        "450",
        "200",
        "",
        "",
    ])

    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))
    monkeypatch.setattr(
        simple_gui.ConfigurationValidator,
        "validate",
        lambda config: (False, ["bad config"]),
    )

    result = simple_gui.ConsoleConfig().show_config(config)

    assert result is None
    output = capsys.readouterr().out
    assert "apenas números" in output
    assert "Opção inválida" in output
    assert "Velocidade deve ser um número" in output
    assert "Velocidade deve estar entre 50 e 400" in output
    assert "bad config" in output


def test_initial_setup_gui_uses_console_when_tkinter_is_unavailable(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    expected = {"skip_discord": True}

    monkeypatch.setattr(simple_gui, "TKINTER_AVAILABLE", False)
    monkeypatch.setattr(gui, "_console_initial_setup", lambda: expected)

    assert gui.show_initial_setup() == expected


def test_initial_setup_gui_falls_back_to_console_on_exception(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    expected = {"skip_discord": False}

    monkeypatch.setattr(simple_gui, "TKINTER_AVAILABLE", True)
    monkeypatch.setattr(simple_gui, "tk", SimpleNamespace(Tk=lambda: (_ for _ in ()).throw(RuntimeError("boom"))))
    monkeypatch.setattr(gui, "_console_initial_setup", lambda: expected)

    assert gui.show_initial_setup() == expected


def test_initial_setup_gui_show_initial_setup_builds_modal_window(monkeypatch):
    gui = simple_gui.InitialSetupGUI()

    monkeypatch.setattr(simple_gui, "TKINTER_AVAILABLE", True)
    monkeypatch.setattr(simple_gui, "tk", build_fake_tk_module())
    monkeypatch.setattr(gui, "_create_initial_setup_widgets", lambda: setattr(gui, "result", {"ok": True}))

    result = gui.show_initial_setup()

    assert result == {"ok": True}
    assert gui.root.title_value == "TTS Hotkey - Configuração Inicial"
    assert gui.root.resizable_args == (False, False)
    assert gui.root.transient_called is True
    assert gui.root.grab_set_called is True
    assert gui.root.mainloop_called is True


def test_initial_setup_gui_create_widgets_populates_variables(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()

    monkeypatch.setenv("DISCORD_BOT_URL", "http://env-bot")
    monkeypatch.setattr(simple_gui, "tk", build_fake_tk_module())
    monkeypatch.setattr(simple_gui, "ttk", build_fake_ttk_module())

    gui._create_initial_setup_widgets()

    assert gui.member_id_var.get() == ""
    assert gui.guild_id_var.get() == ""
    assert gui.channel_id_var.get() == ""
    assert gui.bot_url_var.get() == "http://env-bot"


def test_initial_setup_gui_skip_discord_sets_result_and_destroys_root(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()

    monkeypatch.setenv("DISCORD_BOT_URL", "http://bot")

    gui._skip_discord()

    assert gui.result == {
        "member_id": None,
        "guild_id": None,
        "channel_id": None,
        "bot_url": "http://bot",
        "skip_discord": True,
    }
    assert gui.root.destroy_called is True


def test_initial_setup_gui_save_and_continue_validates_member_id(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("abc")
    gui.guild_id_var = DummyVar("")
    gui.channel_id_var = DummyVar("")
    gui.bot_url_var = DummyVar("http://bot")
    errors = []

    monkeypatch.setattr(simple_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    gui._save_and_continue()

    assert gui.result is None
    assert errors == [("Erro", "Discord User ID deve conter apenas números!")]


def test_initial_setup_gui_save_and_continue_validates_channel_id(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("")
    gui.channel_id_var = DummyVar("abc")
    gui.bot_url_var = DummyVar("http://bot")
    errors = []

    monkeypatch.setattr(simple_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    gui._save_and_continue()

    assert gui.result is None
    assert errors == [("Erro", "Channel ID deve conter apenas números!")]


def test_initial_setup_gui_save_and_continue_validates_guild_id(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("abc")
    gui.channel_id_var = DummyVar("")
    gui.bot_url_var = DummyVar("http://bot")
    errors = []

    monkeypatch.setattr(simple_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    gui._save_and_continue()

    assert gui.result is None
    assert errors == [("Erro", "Guild ID deve conter apenas números!")]


def test_initial_setup_gui_save_and_continue_requires_bot_url(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("789")
    gui.channel_id_var = DummyVar("456")
    gui.bot_url_var = DummyVar("   ")
    errors = []

    monkeypatch.setattr(simple_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    gui._save_and_continue()

    assert gui.result is None
    assert errors == [("Erro", "Bot URL é obrigatória!")]


def test_initial_setup_gui_save_and_continue_requires_guild_id_for_discord(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("   ")
    gui.channel_id_var = DummyVar("456")
    gui.bot_url_var = DummyVar("http://bot")
    errors = []

    monkeypatch.setattr(simple_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    gui._save_and_continue()

    assert gui.result is None
    assert errors == [("Erro", "Guild ID é obrigatória para usar o bot do Discord!")]


def test_initial_setup_gui_save_and_continue_with_member_id(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("789")
    gui.channel_id_var = DummyVar("456")
    gui.bot_url_var = DummyVar("http://bot")
    infos = []

    monkeypatch.setattr(simple_gui.messagebox, "showinfo", lambda title, message: infos.append((title, message)))

    gui._save_and_continue()

    assert gui.result == {
        "member_id": "123",
        "guild_id": "789",
        "channel_id": "456",
        "bot_url": "http://bot",
        "skip_discord": False,
    }
    assert infos == [("Sucesso", "Configuração salva! O TTS funcionará no Discord.")]
    assert gui.root.destroy_called is True


def test_initial_setup_gui_save_and_continue_without_member_id(monkeypatch):
    gui = simple_gui.InitialSetupGUI()
    gui.root = DummyRoot()
    gui.member_id_var = DummyVar("   ")
    gui.guild_id_var = DummyVar("   ")
    gui.channel_id_var = DummyVar("")
    gui.bot_url_var = DummyVar("http://bot")
    infos = []

    monkeypatch.setattr(simple_gui.messagebox, "showinfo", lambda title, message: infos.append((title, message)))

    gui._save_and_continue()

    assert gui.result == {
        "member_id": None,
        "guild_id": None,
        "channel_id": None,
        "bot_url": "http://bot",
        "skip_discord": False,
    }
    assert infos == [("Aviso", "Sem Discord User ID, o TTS funcionará apenas localmente.")]


def test_console_initial_setup_handles_invalid_ids_and_defaults(monkeypatch, capsys):
    gui = simple_gui.InitialSetupGUI()
    responses = iter(["abc", "xyz", "qwe", ""])

    monkeypatch.setenv("DISCORD_BOT_URL", "http://default-bot")
    monkeypatch.setattr("builtins.input", lambda _prompt: next(responses))

    result = gui._console_initial_setup()

    assert result == {
        "member_id": None,
        "guild_id": None,
        "channel_id": None,
        "bot_url": "http://default-bot",
        "skip_discord": True,
    }
    output = capsys.readouterr().out
    assert "ID deve conter apenas números" in output
    assert "TTS funcionará apenas localmente" in output


def test_gui_config_show_config_falls_back_to_console_without_tkinter(monkeypatch, capsys):
    config = StandaloneConfig.create_default()
    expected = StandaloneConfig.create_default()

    monkeypatch.setattr(simple_gui, "TKINTER_AVAILABLE", False)
    monkeypatch.setattr(simple_gui.ConsoleConfig, "show_config", lambda self, config: expected)

    result = simple_gui.GUIConfig().show_config(config)

    assert result is expected
    assert "usando console" in capsys.readouterr().out


def test_gui_config_show_config_creates_window_and_returns_result(monkeypatch):
    gui = simple_gui.GUIConfig()
    config = StandaloneConfig.create_default()

    monkeypatch.setattr(simple_gui, "TKINTER_AVAILABLE", True)
    monkeypatch.setattr(simple_gui, "tk", build_fake_tk_module())
    monkeypatch.setattr(gui, "_create_interface", lambda: setattr(gui, "result", config))

    result = gui.show_config(config)

    assert result is config
    assert gui.root.title_value == "🎤 TTS Hotkey - Configuração"
    assert gui.root.resizable_args == (True, True)
    assert gui.root.update_idletasks_called is True
    assert gui.root.mainloop_called is True


def test_gui_config_create_tabs_populates_variables(monkeypatch):
    gui = simple_gui.GUIConfig()
    gui.root = DummyRoot()
    gui.config = StandaloneConfig.create_default()
    gui.config.discord.member_id = "123"
    gui.config.discord.guild_id = "456"
    gui.config.discord.bot_url = "http://bot"
    gui.config.tts.engine = "pyttsx3"
    gui.config.tts.language = "en"
    gui.config.tts.voice_id = "voice"
    gui.config.tts.rate = 220
    gui.config.hotkey.trigger_open = "["
    gui.config.hotkey.trigger_close = "]"

    monkeypatch.setattr(simple_gui, "tk", build_fake_tk_module())
    monkeypatch.setattr(simple_gui, "ttk", build_fake_ttk_module())

    gui._create_interface()

    assert gui.member_id_var.get() == "123"
    assert gui.guild_id_var.get() == "456"
    assert gui.bot_url_var.get() == "http://bot"
    assert gui.engine_var.get() == "pyttsx3"
    assert gui.language_var.get() == "en"
    assert gui.voice_id_var.get() == "voice"
    assert gui.rate_var.get() == "220"
    assert gui.trigger_open_var.get() == "["
    assert gui.trigger_close_var.get() == "]"


def test_gui_config_save_config_returns_early_when_fields_missing():
    gui = simple_gui.GUIConfig()
    gui.config = StandaloneConfig.create_default()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("456")

    gui._save_config()

    assert gui.result is None


def test_gui_config_save_config_saves_valid_configuration(monkeypatch):
    gui = simple_gui.GUIConfig()
    gui.root = DummyRoot()
    gui.config = StandaloneConfig.create_default()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("456")
    gui.bot_url_var = DummyVar("http://bot")
    gui.engine_var = DummyVar("pyttsx3")
    gui.language_var = DummyVar("en")
    gui.voice_id_var = DummyVar("voice")
    gui.rate_var = DummyVar("210")
    gui.trigger_open_var = DummyVar("[")
    gui.trigger_close_var = DummyVar("]")

    monkeypatch.setattr(simple_gui.ConfigurationValidator, "validate", lambda config: (True, []))

    gui._save_config()

    assert gui.result is not None
    assert gui.result.discord.member_id == "123"
    assert gui.result.discord.guild_id == "456"
    assert gui.result.tts.engine == "pyttsx3"
    assert gui.result.tts.rate == 210
    assert gui.result.hotkey.trigger_open == "["
    assert gui.root.destroy_called is True


def test_gui_config_save_config_shows_validation_errors(monkeypatch):
    gui = simple_gui.GUIConfig()
    gui.config = StandaloneConfig.create_default()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("456")
    gui.bot_url_var = DummyVar("http://bot")
    gui.engine_var = DummyVar("gtts")
    gui.language_var = DummyVar("pt")
    gui.voice_id_var = DummyVar("voice")
    gui.rate_var = DummyVar("180")
    gui.trigger_open_var = DummyVar("{")
    gui.trigger_close_var = DummyVar("}")
    errors = []

    monkeypatch.setattr(simple_gui.ConfigurationValidator, "validate", lambda config: (False, ["bad rate"]))
    monkeypatch.setattr(simple_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    gui._save_config()

    assert gui.result is None
    assert errors == [("Erro de Validação", "Erros encontrados:\n\nbad rate")]


def test_gui_config_save_config_handles_value_error(monkeypatch):
    gui = simple_gui.GUIConfig()
    gui.config = StandaloneConfig.create_default()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("456")
    gui.bot_url_var = DummyVar("http://bot")
    gui.engine_var = DummyVar("gtts")
    gui.language_var = DummyVar("pt")
    gui.voice_id_var = DummyVar("voice")
    gui.rate_var = DummyVar("abc")
    gui.trigger_open_var = DummyVar("{")
    gui.trigger_close_var = DummyVar("}")
    errors = []

    monkeypatch.setattr(simple_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    gui._save_config()

    assert errors
    assert errors[0][0] == "Erro"
    assert "Valor inválido" in errors[0][1]


def test_gui_config_save_config_handles_unexpected_error(monkeypatch):
    gui = simple_gui.GUIConfig()
    gui.config = StandaloneConfig.create_default()
    gui.member_id_var = DummyVar("123")
    gui.guild_id_var = DummyVar("456")
    gui.bot_url_var = DummyVar("http://bot")
    gui.engine_var = DummyVar("gtts")
    gui.language_var = DummyVar("pt")
    gui.voice_id_var = DummyVar("voice")
    gui.rate_var = DummyVar("180")
    gui.trigger_open_var = DummyVar("{")
    gui.trigger_close_var = DummyVar("}")
    errors = []

    monkeypatch.setattr(simple_gui, "replace", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("boom")))
    monkeypatch.setattr(simple_gui.messagebox, "showerror", lambda title, message: errors.append((title, message)))

    gui._save_config()

    assert errors == [("Erro", "Erro inesperado: boom")]


def test_gui_config_cancel_destroys_root():
    gui = simple_gui.GUIConfig()
    gui.root = DummyRoot()
    gui.result = StandaloneConfig.create_default()

    gui._cancel()

    assert gui.result is None
    assert gui.root.destroy_called is True


def test_configuration_service_prefers_gui_and_falls_back_on_error(monkeypatch, capsys):
    config = StandaloneConfig.create_default()
    expected = StandaloneConfig.create_default()

    monkeypatch.setattr(simple_gui, "TKINTER_AVAILABLE", True)
    monkeypatch.setattr(simple_gui.GUIConfig, "show_config", lambda self, config: (_ for _ in ()).throw(RuntimeError("gui fail")))
    monkeypatch.setattr(simple_gui.ConsoleConfig, "show_config", lambda self, config: expected)

    result = simple_gui.ConfigurationService(prefer_gui=True).get_configuration(config)

    assert result is expected
    output = capsys.readouterr().out
    assert "Erro na GUI" in output
    assert "Alternando para console" in output


def test_configuration_service_uses_console_when_gui_not_preferred(monkeypatch):
    config = StandaloneConfig.create_default()
    expected = StandaloneConfig.create_default()

    monkeypatch.setattr(simple_gui.ConsoleConfig, "show_config", lambda self, config: expected)

    result = simple_gui.ConfigurationService(prefer_gui=False).get_configuration(config)

    assert result is expected
