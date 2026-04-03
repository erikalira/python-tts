from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.gui import configuration_service, tk_support


def test_configuration_service_uses_gui_when_preferred_and_available(monkeypatch):
    expected = DesktopAppConfig.create_default()
    current_config = DesktopAppConfig.create_default()
    called = {}

    def fake_show_config(self, config):
        called["config"] = config
        return expected

    monkeypatch.setattr(tk_support, "TKINTER_AVAILABLE", True)
    monkeypatch.setattr(configuration_service.GUIConfig, "show_config", fake_show_config)

    result = configuration_service.ConfigurationService(prefer_gui=True).get_configuration(current_config)

    assert result is expected
    assert called["config"] is current_config


def test_configuration_service_falls_back_to_console_when_gui_is_disabled(monkeypatch):
    expected = DesktopAppConfig.create_default()
    current_config = DesktopAppConfig.create_default()
    called = {}

    def fake_show_config(self, config):
        called["config"] = config
        return expected

    monkeypatch.setattr(tk_support, "TKINTER_AVAILABLE", True)
    monkeypatch.setattr(configuration_service.ConsoleConfig, "show_config", fake_show_config)

    result = configuration_service.ConfigurationService(prefer_gui=False).get_configuration(current_config)

    assert result is expected
    assert called["config"] is current_config


def test_configuration_service_falls_back_to_console_when_gui_raises(monkeypatch):
    expected = DesktopAppConfig.create_default()
    current_config = DesktopAppConfig.create_default()
    called = {}

    def fail_show_config(self, _config):
        raise RuntimeError("boom")

    def fake_console_show_config(self, config):
        called["config"] = config
        return expected

    monkeypatch.setattr(tk_support, "TKINTER_AVAILABLE", True)
    monkeypatch.setattr(configuration_service.GUIConfig, "show_config", fail_show_config)
    monkeypatch.setattr(configuration_service.ConsoleConfig, "show_config", fake_console_show_config)

    result = configuration_service.ConfigurationService(prefer_gui=True).get_configuration(current_config)

    assert result is expected
    assert called["config"] is current_config
