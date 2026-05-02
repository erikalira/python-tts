"""HTTP adapter for sending TTS requests to the Discord bot runtime."""

import logging
from dataclasses import dataclass
from typing import Optional, Protocol

from src.application.dto import (
    BotErrorResponseDTO,
    BotHealthResponseDTO,
    BotSpeakRequestDTO,
    BotVoiceContextResponseDTO,
    DesktopBotConnectionStatusDTO,
    DesktopBotVoiceContextStatusDTO,
)
from src.core.entities import TTSConfig

try:
    import requests

    _requests_available = True
    _request_timeout_error = requests.exceptions.Timeout
except ImportError:  # pragma: no cover - exercised via availability checks
    requests = None
    _requests_available = False
    _request_timeout_error = TimeoutError

from ..config.desktop_config import DesktopAppConfig

logger = logging.getLogger(__name__)

DiscordSpeakRequestDTO = BotSpeakRequestDTO

@dataclass(frozen=True)
class DiscordBotHttpResponse:
    """Minimal normalized HTTP response used by the desktop bot client."""

    ok: bool
    status_code: int
    text: str = ""


class DiscordBotClient(Protocol):
    """Port for sending TTS requests to the Discord bot runtime."""

    def is_available(self) -> bool:
        """Return whether the bot client is ready for requests."""
        ...

    def build_request(self, text: str) -> BotSpeakRequestDTO:
        """Build a speak request from the provided text."""
        ...

    def send_speak_request(self, request: BotSpeakRequestDTO) -> bool:
        """Send a speak request to the Discord bot."""
        ...

    def check_connection(self) -> DesktopBotConnectionStatusDTO:
        """Check whether the bot runtime is reachable."""
        ...

    def fetch_voice_context(self) -> DesktopBotVoiceContextStatusDTO:
        """Fetch the current voice context for the configured member."""
        ...

    def get_last_error_message(self) -> Optional[str]:
        """Return the latest human-readable error from the bot client."""


class DiscordBotHttpTransport:
    """Thin HTTP transport for bot runtime requests."""

    def __init__(self, config: DesktopAppConfig):
        self._config = config

    def post_speak(self, url: str, request_dto: BotSpeakRequestDTO) -> DiscordBotHttpResponse:
        if requests is None:
            raise RuntimeError("requests library is not available")
        response = requests.post(
            url,
            json=request_dto.to_payload(),
            timeout=self._config.network.request_timeout,
            headers=self._build_headers(include_speak_token=True),
        )
        return DiscordBotHttpResponse(
            ok=response.ok,
            status_code=response.status_code,
            text=self._extract_text(response),
        )

    def get_health(self, url: str) -> tuple[DiscordBotHttpResponse, BotHealthResponseDTO | BotErrorResponseDTO | None]:
        if requests is None:
            raise RuntimeError("requests library is not available")
        response = requests.get(
            url,
            timeout=self._config.network.request_timeout,
            headers=self._build_headers(),
        )
        http_response = DiscordBotHttpResponse(
            ok=response.ok,
            status_code=response.status_code,
            text=self._extract_text(response),
        )
        return http_response, self._parse_health_payload(response)

    def get_voice_context(
        self,
        url: str,
        *,
        member_id: str,
    ) -> tuple[DiscordBotHttpResponse, BotVoiceContextResponseDTO | BotErrorResponseDTO | None]:
        if requests is None:
            raise RuntimeError("requests library is not available")
        response = requests.get(
            url,
            params={"member_id": member_id},
            timeout=self._config.network.request_timeout,
            headers=self._build_headers(),
        )
        http_response = DiscordBotHttpResponse(
            ok=response.ok,
            status_code=response.status_code,
            text=self._extract_text(response),
        )
        return http_response, self._parse_voice_context_payload(response)

    def _extract_text(self, response) -> str:
        text = getattr(response, "text", "")
        if text is None:
            return ""
        return str(text).strip()

    def _build_headers(self, *, include_speak_token: bool = False) -> dict[str, str]:
        headers = {"User-Agent": self._config.network.user_agent}
        if include_speak_token and self._config.discord.speak_token:
            headers["X-Bot-Token"] = self._config.discord.speak_token
        return headers

    def _extract_payload(self, response) -> dict[str, object] | None:
        try:
            payload = response.json()
        except Exception:
            return None
        if isinstance(payload, dict):
            return payload
        return None

    def _parse_health_payload(self, response) -> BotHealthResponseDTO | BotErrorResponseDTO | None:
        payload = self._extract_payload(response)
        if payload is None:
            return None
        if "status" in payload:
            return BotHealthResponseDTO(status=str(payload.get("status") or "unknown"))
        return BotErrorResponseDTO(
            success=self._parse_optional_bool(payload.get("success")),
            code=self._parse_optional_str(payload.get("code")),
            message=self._parse_optional_str(payload.get("message")),
        )

    def _parse_voice_context_payload(self, response) -> BotVoiceContextResponseDTO | BotErrorResponseDTO | None:
        payload = self._extract_payload(response)
        if payload is None:
            return None
        if "guild_name" in payload or "channel_name" in payload or "member_id" in payload or "code" in payload:
            return BotVoiceContextResponseDTO(
                success=bool(payload.get("success")),
                code=str(payload.get("code") or "unknown"),
                member_id=self._parse_optional_int(payload.get("member_id")),
                guild_id=self._parse_optional_int(payload.get("guild_id")),
                guild_name=self._parse_optional_str(payload.get("guild_name")),
                channel_id=self._parse_optional_int(payload.get("channel_id")),
                channel_name=self._parse_optional_str(payload.get("channel_name")),
                message=self._parse_optional_str(payload.get("message")),
            )
        return BotErrorResponseDTO(
            success=self._parse_optional_bool(payload.get("success")),
            code=self._parse_optional_str(payload.get("code")),
            message=self._parse_optional_str(payload.get("message")),
        )

    def _parse_optional_int(self, value: object) -> int | None:
        if value is None:
            return None
        if not isinstance(value, (str, int, float)):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    def _parse_optional_str(self, value: object) -> str | None:
        if value is None:
            return None
        return str(value)

    def _parse_optional_bool(self, value: object) -> bool | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes"}:
                return True
            if normalized in {"false", "0", "no"}:
                return False
        return bool(value)


class HttpDiscordBotClient:
    """HTTP adapter for the Discord bot speak endpoint."""

    def __init__(self, config: DesktopAppConfig, transport: DiscordBotHttpTransport | None = None):
        self._config = config
        self._transport = transport or DiscordBotHttpTransport(config)
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

    def build_request(self, text: str) -> BotSpeakRequestDTO:
        """Build a speak request from Desktop App configuration."""
        return BotSpeakRequestDTO(
            text=text,
            member_id=self._config.discord.member_id,
            config_override=TTSConfig(
                engine=self._config.tts.engine,
                language=self._config.tts.language,
                voice_id=self._config.tts.voice_id,
                rate=self._config.tts.rate,
            ),
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

    def send_speak_request(self, request: BotSpeakRequestDTO) -> bool:
        """Send a speak request to the configured Discord bot."""
        if not self.is_available():
            logger.debug("[DISCORD_BOT_CLIENT] Bot client unavailable for speak request")
            self._last_error_message = "Bot client is unavailable"
            return False

        logger.info("[DISCORD_BOT_CLIENT] Sending TTS request to Discord bot")

        try:
            response = self._transport.post_speak(self.get_speak_url(), request)
        except _request_timeout_error:
            logger.warning("[DISCORD_BOT_CLIENT] Timeout while connecting to Discord bot")
            self._last_error_message = "Timeout ao conectar no bot"
            return False
        except Exception as exc:
            logger.error("[DISCORD_BOT_CLIENT] Failed to connect to Discord bot: %s", exc)
            self._last_error_message = f"Failed to connect to the bot: {exc}"
            return False

        if response.ok:
            self._last_error_message = None
            logger.info("[DISCORD_BOT_CLIENT] Discord bot accepted the TTS request")
            return True

        self._last_error_message = self._build_http_error_message(
            response.status_code,
            response.text,
        )
        logger.warning(
            "[DISCORD_BOT_CLIENT] Discord bot returned HTTP %s: %s",
            response.status_code,
            response.text or "<no response body>",
        )
        return False

    def check_connection(self) -> DesktopBotConnectionStatusDTO:
        """Check whether the bot runtime is reachable and healthy."""
        if not self.has_transport():
            return DesktopBotConnectionStatusDTO(
                success=False,
                message="requests library is not available",
            )

        if not self._config.discord.bot_url:
            return DesktopBotConnectionStatusDTO(success=False, message="Bot URL is not configured")

        try:
            response, payload = self._transport.get_health(self.get_health_url())
        except _request_timeout_error:
            logger.warning("[DISCORD_BOT_CLIENT] Timeout while checking bot health")
            return DesktopBotConnectionStatusDTO(success=False, message="Timeout ao conectar no bot")
        except Exception as exc:
            logger.error("[DISCORD_BOT_CLIENT] Failed to check bot health: %s", exc)
            return DesktopBotConnectionStatusDTO(success=False, message=f"Failed to connect: {exc}")

        if response.ok:
            return DesktopBotConnectionStatusDTO(
                success=True,
                message=(
                    "Bot connection validated successfully"
                    if not isinstance(payload, BotHealthResponseDTO) or payload.status == "healthy"
                    else f"Bot returned status {payload.status}"
                ),
            )

        return DesktopBotConnectionStatusDTO(
            success=False,
            message=f"Bot returned HTTP {response.status_code}",
        )

    def fetch_voice_context(self) -> DesktopBotVoiceContextStatusDTO:
        """Fetch the current guild/channel detected for the configured member."""
        if not self.has_transport():
            return DesktopBotVoiceContextStatusDTO(
                success=False,
                message="requests library is not available",
            )

        if not self._config.discord.bot_url:
            return DesktopBotVoiceContextStatusDTO(success=False, message="Bot URL is not configured")

        if not self._config.discord.member_id:
            return DesktopBotVoiceContextStatusDTO(success=False, message="User ID is not configured")

        try:
            response, payload = self._transport.get_voice_context(
                self.get_voice_context_url(),
                member_id=self._config.discord.member_id,
            )
        except _request_timeout_error:
            logger.warning("[DISCORD_BOT_CLIENT] Timeout while fetching voice context")
            return DesktopBotVoiceContextStatusDTO(
                success=False,
                message="Timed out while checking the voice channel",
            )
        except Exception as exc:
            logger.error("[DISCORD_BOT_CLIENT] Failed to fetch voice context: %s", exc)
            return DesktopBotVoiceContextStatusDTO(
                success=False,
                message=f"Failed to check the voice channel: {exc}",
            )

        if response.ok and isinstance(payload, BotVoiceContextResponseDTO):
            guild_name = payload.guild_name or "Unknown server"
            channel_name = payload.channel_name or "Unknown channel"
            return DesktopBotVoiceContextStatusDTO(
                success=True,
                message=f"Detected channel: {guild_name} / {channel_name}",
                guild_name=guild_name,
                guild_id=payload.guild_id,
                channel_name=channel_name,
                channel_id=payload.channel_id,
            )

        if (
            response.status_code == 404
            and isinstance(payload, BotVoiceContextResponseDTO)
            and payload.code == "not_in_channel"
        ):
            return DesktopBotVoiceContextStatusDTO(
                success=False,
                message="User is not connected to any voice channel",
            )

        if response.status_code == 404:
            return DesktopBotVoiceContextStatusDTO(
                success=False,
                message="Channel detection endpoint is not available on the bot. Update the bot.",
            )

        message = None
        if isinstance(payload, (BotVoiceContextResponseDTO, BotErrorResponseDTO)):
            message = payload.message
        if not message:
            message = f"Bot returned HTTP {response.status_code}"
        return DesktopBotVoiceContextStatusDTO(success=False, message=message)

    def get_last_error_message(self) -> Optional[str]:
        """Return the latest human-readable error from the bot client."""
        return self._last_error_message

    def _build_http_error_message(self, status_code: int, response_text: str) -> str:
        """Build a user-facing error message from an HTTP failure."""
        normalized_text = response_text.lower()
        if status_code == 503 and "service suspended" in normalized_text:
            return "Bot returned HTTP 503: service is suspended or unavailable"
        if response_text:
            return f"Bot returned HTTP {status_code}: {response_text}"
        return f"Bot returned HTTP {status_code}"
