"""Presentation helpers for the Desktop App main window."""

from __future__ import annotations

from dataclasses import dataclass

from src.application.dto import DesktopBotActionResultDTO
from ..config.desktop_config import DesktopAppConfig

SUCCESS_COLOR = "#155724"
WARNING_COLOR = "#856404"
ERROR_COLOR = "#721c24"


@dataclass(frozen=True)
class MainWindowMessage:
    """View-ready text and color for a main-window status field."""

    text: str
    color: str


class DesktopAppMainWindowPresenter:
    """Build user-facing messages for the Desktop App main window."""

    def initial_status(self) -> MainWindowMessage:
        return MainWindowMessage(
            text="Fill in the fields, test the connection, and keep the window open while using the app.",
            color=SUCCESS_COLOR,
        )

    def initial_connection(self) -> MainWindowMessage:
        return MainWindowMessage(
            text="Connection not tested yet",
            color=WARNING_COLOR,
        )

    def initial_voice_context(self) -> MainWindowMessage:
        return MainWindowMessage(
            text="Detected channel has not been checked yet",
            color=WARNING_COLOR,
        )

    def build_status(self, message: str, success: bool) -> MainWindowMessage:
        prefix = "OK:" if success else "Attention:"
        return MainWindowMessage(
            text=f"{prefix} {message}",
            color=SUCCESS_COLOR if success else ERROR_COLOR,
        )

    def build_connection_result(self, result: DesktopBotActionResultDTO, default_message: str) -> MainWindowMessage:
        return MainWindowMessage(
            text=result.message or default_message,
            color=SUCCESS_COLOR if result.success else ERROR_COLOR,
        )

    def build_invalid_value_message(self, action_name: str, exc: ValueError) -> MainWindowMessage:
        return MainWindowMessage(
            text=f"{action_name} failed: invalid value ({exc})",
            color=ERROR_COLOR,
        )

    def build_local_config_status(self, config: DesktopAppConfig) -> MainWindowMessage:
        is_discord_ready = bool(config.discord.bot_url and config.discord.member_id)
        if is_discord_ready:
            return MainWindowMessage(
                text="Bot configured: URL and User ID filled.",
                color=SUCCESS_COLOR,
            )

        message = "Incomplete configuration: fill Bot URL and User ID to use the bot."
        if config.interface.local_tts_enabled:
            message += " Optional local voice enabled as fallback."
        else:
            message += " Optional local voice disabled."

        return MainWindowMessage(text=message, color=WARNING_COLOR)
