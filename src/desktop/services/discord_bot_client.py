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

from ..config.desktop_config import DesktopAppConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscordSpeakRequest:
    """Payload for the Discord bot speak endpoint."""

    text: str
    member_id: Optional[str] = None

    def to_payload(self) -> dict:
        """Serialize request to the JSON payload expected by the bot."""
        payload = {"text": self.text}
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

    def fetch_voice_context(self) -> dict:
        """Fetch the current voice context for the configured member."""

    def get_last_error_message(self) -> Optional[str]:
        """Return the latest human-readable error from the bot client."""


class HttpDiscordBotClient:
    """HTTP adapter for the Discord bot speak endpoint."""

    def __init__(self, config: DesktopAppConfig):
        self._config = config
        self._last_error_message: Optional[str] = None

    def is_available(self) -> bool:
        """Check whether HTTP requests can be sent to the bot."""
        return _requests_available and bool(self._config.discord.bot_url)

    def has_bot_url(self) -> bool:
        """Return whether the bot base URL is configured."""
        return bool(self._config.discord.bot_url)

    def has_member_id(self) -> bool:
        """Return whether the Desktop App has a configured Discord member."""
        return bool(self._config.discord.member_id)

    def has_transport(self) -> bool:
        """Return whether the HTTP transport dependency is installed."""
        return _requests_available

    def build_request(self, text: str) -> DiscordSpeakRequest:
        """Build a speak request from Desktop App configuration."""
        return DiscordSpeakRequest(
            text=text,
            member_id=self._config.discord.member_id,
        )

    def send_text(self, text: str) -> bool:
        """Build and send a text payload through the bot runtime."""
        return self.send_speak_request(self.build_request(text))

    def get_speak_url(self) -> str:
        """Return the bot speak endpoint URL."""
        return self._config.discord.bot_url.rstrip("/") + "/speak"

    def get_health_url(self) -> str:
        """Return the bot health endpoint URL."""
        return self._config.discord.bot_url.rstrip("/") + "/health"

    def get_voice_context_url(self) -> str:
        """Return the bot voice-context endpoint URL."""
        return self._config.discord.bot_url.rstrip("/") + "/voice-context"

    def send_speak_request(self, request: DiscordSpeakRequest) -> bool:
        """Send a speak request to the configured Discord bot."""
        if not self.is_available():
            logger.debug("[DISCORD_BOT_CLIENT] Bot client unavailable for speak request")
            self._last_error_message = "Cliente do bot indisponivel"
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
            self._last_error_message = "Timeout ao conectar no bot"
            return False
        except Exception as exc:
            logger.error(f"[DISCORD_BOT_CLIENT] Failed to connect to Discord bot: {exc}")
            self._last_error_message = f"Falha ao conectar no bot: {exc}"
            return False

        if response.ok:
            self._last_error_message = None
            logger.info("[DISCORD_BOT_CLIENT] Discord bot accepted the TTS request")
            return True

        response_text = self._extract_response_text(response)
        self._last_error_message = self._build_http_error_message(
            response.status_code,
            response_text,
        )
        logger.warning(
            "[DISCORD_BOT_CLIENT] Discord bot returned HTTP %s: %s",
            response.status_code,
            response_text or "<no response body>",
        )
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

    def fetch_voice_context(self) -> dict:
        """Fetch the current guild/channel detected for the configured member."""
        if not self.has_transport():
            return {"success": False, "message": "Biblioteca requests nao esta disponivel"}

        if not self._config.discord.bot_url:
            return {"success": False, "message": "Bot URL nao configurada"}

        if not self._config.discord.member_id:
            return {"success": False, "message": "User ID nao configurado"}

        try:
            response = requests.get(
                self.get_voice_context_url(),
                params={"member_id": self._config.discord.member_id},
                timeout=self._config.network.request_timeout,
                headers={"User-Agent": self._config.network.user_agent},
            )
        except requests.exceptions.Timeout:
            logger.warning("[DISCORD_BOT_CLIENT] Timeout while fetching voice context")
            return {"success": False, "message": "Timeout ao consultar canal de voz"}
        except Exception as exc:
            logger.error(f"[DISCORD_BOT_CLIENT] Failed to fetch voice context: {exc}")
            return {"success": False, "message": f"Falha ao consultar canal de voz: {exc}"}

        try:
            payload = response.json()
        except Exception:
            payload = {}

        if response.ok:
            guild_name = payload.get("guild_name") or "Servidor desconhecido"
            channel_name = payload.get("channel_name") or "Canal desconhecido"
            guild_id = payload.get("guild_id")
            channel_id = payload.get("channel_id")
            return {
                "success": True,
                "message": f"Canal detectado: {guild_name} / {channel_name}",
                "guild_name": guild_name,
                "guild_id": guild_id,
                "channel_name": channel_name,
                "channel_id": channel_id,
            }

        if response.status_code == 404 and payload.get("code") == "not_in_channel":
            return {
                "success": False,
                "message": "Usuario nao esta conectado a nenhum canal de voz",
            }

        if response.status_code == 404:
            return {
                "success": False,
                "message": "Endpoint de deteccao de canal nao esta disponivel no bot. Atualize o bot.",
            }

        message = payload.get("message") if isinstance(payload, dict) else None
        if not message:
            message = f"Bot respondeu HTTP {response.status_code}"
        return {"success": False, "message": message}

    def get_last_error_message(self) -> Optional[str]:
        """Return the latest human-readable error from the bot client."""
        return self._last_error_message

    def _extract_response_text(self, response) -> str:
        """Safely read and normalize the bot response body for diagnostics."""
        text = getattr(response, "text", "")
        if text is None:
            return ""
        return str(text).strip()

    def _build_http_error_message(self, status_code: int, response_text: str) -> str:
        """Build a user-facing error message from an HTTP failure."""
        if response_text:
            return f"Bot respondeu HTTP {status_code}: {response_text}"
        return f"Bot respondeu HTTP {status_code}"
