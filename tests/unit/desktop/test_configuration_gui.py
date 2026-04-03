from types import SimpleNamespace

from src.desktop.config.desktop_config import DesktopAppConfig, get_default_discord_bot_url
from src.desktop.gui import configuration_gui


def test_console_configuration_interface_delegates_to_console_config(monkeypatch):
    expected = DesktopAppConfig.create_default()
    current_config = DesktopAppConfig.create_default()
    called = {}

    def fake_show_config(self, config):
        called["config"] = config
        return expected

    monkeypatch.setattr(configuration_gui.ConsoleConfig, "show_config", fake_show_config)

    result = configuration_gui.ConsoleConfigurationInterface().show_configuration_dialog(current_config)

    assert result is expected
    assert called["config"] is current_config


def test_gui_configuration_interface_delegates_to_gui_config(monkeypatch):
    expected = DesktopAppConfig.create_default()
    current_config = DesktopAppConfig.create_default()
    called = {}

    def fake_show_config(self, config):
        called["config"] = config
        return expected

    monkeypatch.setattr(configuration_gui.GUIConfig, "show_config", fake_show_config)

    result = configuration_gui.GUIConfigurationInterface().show_configuration_dialog(current_config)

    assert result is expected
    assert called["config"] is current_config


def test_configuration_ui_factory_respects_preference(monkeypatch):
    monkeypatch.setattr(configuration_gui, "_tkinter_available", True)
    assert isinstance(configuration_gui.ConfigurationUIFactory.create_interface(), configuration_gui.GUIConfigurationInterface)
    assert isinstance(configuration_gui.ConfigurationUIFactory.create_interface(prefer_gui=False), configuration_gui.ConsoleConfigurationInterface)


def test_configuration_display_service_shows_local_mode_without_optional_dependencies(monkeypatch, capsys):
    service = configuration_gui.ConfigurationDisplayService()
    config = DesktopAppConfig.create_default()
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
    assert "SYSTEM TRAY:" in output.upper()
    assert "❌" in output


def test_configuration_display_service_shows_discord_mode_when_requests_is_available(monkeypatch, capsys):
    service = configuration_gui.ConfigurationDisplayService()
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = get_default_discord_bot_url()
    config.discord.member_id = "123"

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
    assert "SYSTEM TRAY:" in output.upper()
    assert "✅" in output

