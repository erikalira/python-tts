"""Application use cases for Desktop App interactions with the bot runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol

DESKTOP_BOT_TEST_MESSAGE = "Teste rapido do Desktop App."


@dataclass(frozen=True)
class DesktopBotConnectionStatus:
    """Structured health-check response from the bot runtime."""

    success: bool
    message: str


@dataclass(frozen=True)
class DesktopBotVoiceContextStatus:
    """Structured voice-context response from the bot runtime."""

    success: bool
    message: str
    guild_name: str | None = None
    guild_id: int | None = None
    channel_name: str | None = None
    channel_id: int | None = None


@dataclass(frozen=True)
class DesktopBotActionResult:
    """Structured result for Desktop App actions against the bot runtime."""

    success: bool
    message: str


@dataclass(frozen=True)
class DesktopBotVoiceContextResult(DesktopBotActionResult):
    """Structured result for Desktop App voice-context detection."""

    guild_name: str | None = None
    channel_name: str | None = None


class DesktopBotGateway(Protocol):
    """Port for Desktop App operations against the bot runtime."""

    def has_bot_url(self) -> bool:
        """Return whether the bot base URL is configured."""

    def has_member_id(self) -> bool:
        """Return whether the configured Discord member is available."""

    def check_connection(self) -> DesktopBotConnectionStatus:
        """Check whether the bot runtime is reachable."""

    def send_text(self, text: str) -> bool:
        """Send a text payload to the bot runtime."""

    def fetch_voice_context(self) -> DesktopBotVoiceContextStatus:
        """Fetch the current detected voice context."""

    def get_last_error_message(self) -> Optional[str]:
        """Return the last human-readable error message."""


class CheckDesktopBotConnectionUseCase:
    """Validate whether the Desktop App can reach the bot runtime."""

    def __init__(self, gateway: DesktopBotGateway):
        self._gateway = gateway

    def execute(self) -> DesktopBotActionResult:
        """Execute the bot health check flow."""
        if not self._gateway.has_bot_url():
            return DesktopBotActionResult(success=False, message="Bot URL nao configurada")

        payload = self._gateway.check_connection()
        return DesktopBotActionResult(
            success=payload.success,
            message=payload.message,
        )


class SendDesktopBotTestMessageUseCase:
    """Send a short Desktop App test message through the bot runtime."""

    def __init__(self, gateway: DesktopBotGateway, test_message: str = DESKTOP_BOT_TEST_MESSAGE):
        self._gateway = gateway
        self._test_message = test_message

    def execute(self) -> DesktopBotActionResult:
        """Send the configured test message and return a neutral result."""
        if not self._gateway.has_bot_url():
            return DesktopBotActionResult(
                success=False,
                message="Bot URL nao configurada para envio de teste",
            )
        if not self._gateway.has_member_id():
            return DesktopBotActionResult(
                success=False,
                message="User ID e necessario para enviar o teste",
            )

        success = self._gateway.send_text(self._test_message)
        if success:
            return DesktopBotActionResult(
                success=True,
                message="Mensagem de teste enviada ao bot com sucesso",
            )

        error_message = (
            self._gateway.get_last_error_message()
            or "Nao foi possivel enviar a mensagem de teste ao bot"
        )
        return DesktopBotActionResult(success=False, message=error_message)


class FetchDesktopBotVoiceContextUseCase:
    """Query the current detected voice context for the configured member."""

    def __init__(self, gateway: DesktopBotGateway):
        self._gateway = gateway

    def execute(self) -> DesktopBotVoiceContextResult:
        """Fetch the current voice context using the injected gateway."""
        if not self._gateway.has_bot_url():
            return DesktopBotVoiceContextResult(
                success=False,
                message="Bot URL nao configurada para detectar o canal",
            )
        if not self._gateway.has_member_id():
            return DesktopBotVoiceContextResult(
                success=False,
                message="User ID e necessario para detectar o canal",
            )

        payload = self._gateway.fetch_voice_context()
        return DesktopBotVoiceContextResult(
            success=payload.success,
            message=payload.message,
            guild_name=payload.guild_name,
            channel_name=payload.channel_name,
        )
