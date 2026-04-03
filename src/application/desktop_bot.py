"""Application use cases for Desktop App interactions with the bot runtime."""

from __future__ import annotations

from typing import Optional, Protocol

DESKTOP_BOT_TEST_MESSAGE = "Teste rapido do Desktop App."


class DesktopBotGateway(Protocol):
    """Port for Desktop App operations against the bot runtime."""

    def has_bot_url(self) -> bool:
        """Return whether the bot base URL is configured."""

    def has_member_id(self) -> bool:
        """Return whether the configured Discord member is available."""

    def check_connection(self) -> dict:
        """Check whether the bot runtime is reachable."""

    def send_text(self, text: str) -> bool:
        """Send a text payload to the bot runtime."""

    def fetch_voice_context(self) -> dict:
        """Fetch the current detected voice context."""

    def get_last_error_message(self) -> Optional[str]:
        """Return the last human-readable error message."""


class CheckDesktopBotConnectionUseCase:
    """Validate whether the Desktop App can reach the bot runtime."""

    def __init__(self, gateway: DesktopBotGateway):
        self._gateway = gateway

    def execute(self) -> dict:
        """Execute the bot health check flow."""
        if not self._gateway.has_bot_url():
            return {"success": False, "message": "Bot URL nao configurada"}
        return self._gateway.check_connection()


class SendDesktopBotTestMessageUseCase:
    """Send a short Desktop App test message through the bot runtime."""

    def __init__(self, gateway: DesktopBotGateway, test_message: str = DESKTOP_BOT_TEST_MESSAGE):
        self._gateway = gateway
        self._test_message = test_message

    def execute(self) -> dict:
        """Send the configured test message and return a neutral result."""
        if not self._gateway.has_bot_url():
            return {"success": False, "message": "Bot URL nao configurada para envio de teste"}
        if not self._gateway.has_member_id():
            return {"success": False, "message": "User ID e necessario para enviar o teste"}

        success = self._gateway.send_text(self._test_message)
        if success:
            return {"success": True, "message": "Mensagem de teste enviada ao bot com sucesso"}

        error_message = (
            self._gateway.get_last_error_message()
            or "Nao foi possivel enviar a mensagem de teste ao bot"
        )
        return {"success": False, "message": error_message}


class FetchDesktopBotVoiceContextUseCase:
    """Query the current detected voice context for the configured member."""

    def __init__(self, gateway: DesktopBotGateway):
        self._gateway = gateway

    def execute(self) -> dict:
        """Fetch the current voice context using the injected gateway."""
        if not self._gateway.has_bot_url():
            return {"success": False, "message": "Bot URL nao configurada para detectar o canal"}
        if not self._gateway.has_member_id():
            return {"success": False, "message": "User ID e necessario para detectar o canal"}
        return self._gateway.fetch_voice_context()
