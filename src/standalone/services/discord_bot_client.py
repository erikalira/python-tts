"""HTTP adapter for sending TTS requests to the Discord bot runtime."""

import logging
from dataclasses import dataclass
from typing import Optional, Protocol

try:
    import requests
    _requests_available = True
except ImportError:  # pragma: no cover - exercised via availability checks
    requests = None
    _requests_available = False

from ..config.standalone_config import StandaloneConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscordSpeakRequest:
    """Payload for the Discord bot speak endpoint."""

    text: str
    guild_id: Optional[str] = None
    channel_id: Optional[str] = None
    member_id: Optional[str] = None

    def to_payload(self) -> dict:
        """Serialize request to the JSON payload expected by the bot."""
        payload = {"text": self.text}
        if self.guild_id:
            payload["guild_id"] = self.guild_id
        if self.channel_id:
            payload["channel_id"] = self.channel_id
        if self.member_id:
            payload["member_id"] = self.member_id
        return payload


class DiscordBotClient(Protocol):
    """Port for sending TTS requests to the Discord bot runtime."""

    def is_available(self) -> bool:
        """Return whether the bot client is ready for requests."""

    def build_request(self, text: str) -> DiscordSpeakRequest:
        """Build a speak request from the provided text."""

    def send_speak_request(self, request: DiscordSpeakRequest) -> bool:
        """Send a speak request to the Discord bot."""

    def check_connection(self) -> dict:
        """Check whether the bot runtime is reachable."""


class HttpDiscordBotClient:
    """HTTP adapter for the Discord bot speak endpoint."""

    def __init__(self, config: StandaloneConfig):
        self._config = config

    def is_available(self) -> bool:
        """Check whether HTTP requests can be sent to the bot."""
        return _requests_available and bool(self._config.discord.bot_url)

    def has_transport(self) -> bool:
        """Return whether the HTTP transport dependency is installed."""
        return _requests_available

    def build_request(self, text: str) -> DiscordSpeakRequest:
        """Build a speak request from standalone configuration."""
        return DiscordSpeakRequest(
            text=text,
            guild_id=self._config.discord.guild_id,
            channel_id=self._config.discord.channel_id,
            member_id=self._config.discord.member_id,
        )

    def get_speak_url(self) -> str:
        """Return the bot speak endpoint URL."""
        return self._config.discord.bot_url.rstrip("/") + "/speak"

    def get_health_url(self) -> str:
        """Return the bot health endpoint URL."""
        return self._config.discord.bot_url.rstrip("/") + "/health"

    def send_speak_request(self, request: DiscordSpeakRequest) -> bool:
        """Send a speak request to the configured Discord bot."""
        if not self.is_available():
            logger.debug("[DISCORD_BOT_CLIENT] Bot client unavailable for speak request")
            return False

        payload = request.to_payload()
        logger.info("[DISCORD_BOT_CLIENT] Sending TTS request to Discord bot")

        try:
            response = requests.post(
                self.get_speak_url(),
                json=payload,
                timeout=self._config.network.request_timeout,
                headers={"User-Agent": self._config.network.user_agent},
            )
        except requests.exceptions.Timeout:
            logger.warning("[DISCORD_BOT_CLIENT] Timeout while connecting to Discord bot")
            return False
        except Exception as exc:
            logger.error(f"[DISCORD_BOT_CLIENT] Failed to connect to Discord bot: {exc}")
            return False

        if response.ok:
            logger.info("[DISCORD_BOT_CLIENT] Discord bot accepted the TTS request")
            return True

        logger.warning(f"[DISCORD_BOT_CLIENT] Discord bot returned HTTP {response.status_code}")
        return False

    def check_connection(self) -> dict:
        """Check whether the bot runtime is reachable and healthy."""
        if not self.has_transport():
            return {"success": False, "message": "Biblioteca requests não está disponível"}

        if not self._config.discord.bot_url:
            return {"success": False, "message": "Bot URL não configurada"}

        try:
            response = requests.get(
                self.get_health_url(),
                timeout=self._config.network.request_timeout,
                headers={"User-Agent": self._config.network.user_agent},
            )
        except requests.exceptions.Timeout:
            logger.warning("[DISCORD_BOT_CLIENT] Timeout while checking bot health")
            return {"success": False, "message": "Timeout ao conectar no bot"}
        except Exception as exc:
            logger.error(f"[DISCORD_BOT_CLIENT] Failed to check bot health: {exc}")
            return {"success": False, "message": f"Falha ao conectar: {exc}"}

        if response.ok:
            return {"success": True, "message": "Conexão com o bot validada com sucesso"}

        return {
            "success": False,
            "message": f"Bot respondeu HTTP {response.status_code}",
        }
