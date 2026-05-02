from src.desktop.config.desktop_config import DesktopAppConfig
from src.desktop.gui.main_window_presenter import (
    ERROR_COLOR,
    SUCCESS_COLOR,
    WARNING_COLOR,
    DesktopAppMainWindowPresenter,
)


def test_main_window_presenter_builds_success_status():
    presenter = DesktopAppMainWindowPresenter()

    message = presenter.build_status("Configuration saved", success=True)

    assert message.text == "OK: Configuration saved"
    assert message.color == SUCCESS_COLOR


def test_main_window_presenter_builds_incomplete_config_message_with_local_fallback():
    presenter = DesktopAppMainWindowPresenter()
    config = DesktopAppConfig.create_default()
    config.interface.local_tts_enabled = True

    message = presenter.build_local_config_status(config)

    assert "Incomplete configuration" in message.text
    assert "fallback" in message.text
    assert message.color == WARNING_COLOR


def test_main_window_presenter_builds_ready_config_message():
    presenter = DesktopAppMainWindowPresenter()
    config = DesktopAppConfig.create_default()
    config.discord.bot_url = "http://bot"
    config.discord.member_id = "123"

    message = presenter.build_local_config_status(config)

    assert message.text == "Bot configured: URL and User ID filled."
    assert message.color == SUCCESS_COLOR


def test_main_window_presenter_builds_invalid_value_message():
    presenter = DesktopAppMainWindowPresenter()

    message = presenter.build_invalid_value_message("Test", ValueError("port"))

    assert message.text == "Test failed: invalid value (port)"
    assert message.color == ERROR_COLOR
