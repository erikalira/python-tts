from unittest.mock import Mock

from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.gui import configuration_service, tk_support


def test_configuration_service_uses_gui_when_preferred_and_available(monkeypatch):
    expected = DesktopAppConfig.create_default()
    current_config = DesktopAppConfig.create_default()
    gui = Mock()
    gui.show_config.return_value = expected

    monkeypatch.setattr(tk_support, "TKINTER_AVAILABLE", True)
    service = configuration_service.ConfigurationService(
        prefer_gui=True,
        gui_factory=lambda: gui,
    )

    result = service.get_configuration(current_config)

    assert result is expected
    gui.show_config.assert_called_once_with(current_config)


def test_configuration_service_falls_back_to_console_when_gui_is_disabled(monkeypatch):
    expected = DesktopAppConfig.create_default()
    current_config = DesktopAppConfig.create_default()
    console = Mock()
    console.show_config.return_value = expected

    monkeypatch.setattr(tk_support, "TKINTER_AVAILABLE", True)
    service = configuration_service.ConfigurationService(
        prefer_gui=False,
        console_factory=lambda: console,
    )

    result = service.get_configuration(current_config)

    assert result is expected
    console.show_config.assert_called_once_with(current_config)


def test_configuration_service_falls_back_to_console_when_gui_raises(monkeypatch):
    expected = DesktopAppConfig.create_default()
    current_config = DesktopAppConfig.create_default()
    gui = Mock()
    gui.show_config.side_effect = RuntimeError("boom")
    console = Mock()
    console.show_config.return_value = expected

    monkeypatch.setattr(tk_support, "TKINTER_AVAILABLE", True)
    service = configuration_service.ConfigurationService(
        prefer_gui=True,
        gui_factory=lambda: gui,
        console_factory=lambda: console,
    )

    result = service.get_configuration(current_config)

    assert result is expected
    gui.show_config.assert_called_once_with(current_config)
    console.show_config.assert_called_once_with(current_config)
