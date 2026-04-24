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
            text="Preencha os campos, teste a conexao e mantenha a janela aberta durante o uso.",
            color=SUCCESS_COLOR,
        )

    def initial_connection(self) -> MainWindowMessage:
        return MainWindowMessage(
            text="Conexao ainda nao testada",
            color=WARNING_COLOR,
        )

    def initial_voice_context(self) -> MainWindowMessage:
        return MainWindowMessage(
            text="Canal detectado ainda nao consultado",
            color=WARNING_COLOR,
        )

    def build_status(self, message: str, success: bool) -> MainWindowMessage:
        prefix = "OK:" if success else "Atencao:"
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
            text=f"{action_name} falhou: valor invalido ({exc})",
            color=ERROR_COLOR,
        )

    def build_local_config_status(self, config: DesktopAppConfig) -> MainWindowMessage:
        is_discord_ready = bool(config.discord.bot_url and config.discord.member_id)
        if is_discord_ready:
            return MainWindowMessage(
                text="Bot configurado: URL e User ID preenchidos.",
                color=SUCCESS_COLOR,
            )

        message = "Configuracao incompleta: preencha Bot URL e User ID para usar o bot."
        if config.interface.local_tts_enabled:
            message += " Voz local opcional ativada como fallback."
        else:
            message += " Voz local opcional desativada."

        return MainWindowMessage(text=message, color=WARNING_COLOR)
