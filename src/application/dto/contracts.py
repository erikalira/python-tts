"""Explicit DTO contracts shared across application and desktop runtime flows."""

from __future__ import annotations

from dataclasses import dataclass

from src.core.entities import TTSConfig


@dataclass(frozen=True, slots=True)
class DesktopTTSStatusDTO:
    """Availability details for Desktop App TTS engines and dependencies."""

    discord_available: bool
    local_tts_enabled: bool
    local_available: bool
    pyttsx3_installed: bool
    requests_installed: bool
    bot_url_configured: bool


@dataclass(frozen=True, slots=True)
class DesktopTTSServiceStatusDTO:
    """Runtime status exposed by the Desktop App TTS processor."""

    tts_available: bool
    engines_info: DesktopTTSStatusDTO


@dataclass(frozen=True, slots=True)
class DesktopAppRuntimeStatusDTO:
    """Aggregated Desktop App runtime status for tray and UI consumers."""

    initialized: bool
    running: bool
    discord_configured: bool
    hotkey_active: bool
    tts_available: bool
    tray_available: bool


@dataclass(frozen=True, slots=True)
class HotkeyServiceStatusDTO:
    """Detailed hotkey service status."""

    active: bool
    monitoring: bool
    keyboard_available: bool
    trigger_open: str
    trigger_close: str


@dataclass(frozen=True, slots=True)
class HotkeyManagerStatusDTO:
    """High-level hotkey manager status."""

    initialized: bool
    active: bool
    keyboard_available: bool
    monitoring: bool = False
    trigger_open: str | None = None
    trigger_close: str | None = None


@dataclass(frozen=True, slots=True)
class SystemTrayStatusDTO:
    """System tray availability and runtime status."""

    tray_available: bool
    tray_running: bool
    pystray_installed: bool
    notifications_enabled: bool


@dataclass(frozen=True, slots=True)
class AudioQueueItemStatusDTO:
    """View of a single queued audio item."""

    id: str
    user_id: int | None
    status: str
    position: int
    wait_time_seconds: float


@dataclass(frozen=True, slots=True)
class AudioQueueStatusDTO:
    """Queue details for a guild-scoped audio queue."""

    size: int
    items: list[AudioQueueItemStatusDTO]


@dataclass(frozen=True, slots=True)
class DiscordVoiceChannelCacheStatsDTO:
    """Diagnostic cache stats for the Discord voice-channel repository."""

    cached_channels: int
    cached_members: int
    total_tracked: int


@dataclass(frozen=True, slots=True)
class BotSpeakRequestDTO:
    """Wire contract for POST /speak requests sent to the bot runtime."""

    text: str
    member_id: str | None = None
    guild_id: int | None = None
    channel_id: int | None = None
    config_override: TTSConfig | None = None

    def to_payload(self) -> dict[str, object]:
        """Serialize the request into the JSON payload expected by the bot."""
        payload: dict[str, object] = {"text": self.text}
        if self.member_id:
            payload["member_id"] = self.member_id
        if self.guild_id is not None:
            payload["guild_id"] = self.guild_id
        if self.channel_id is not None:
            payload["channel_id"] = self.channel_id
        if self.config_override:
            payload["config_override"] = {
                "engine": self.config_override.engine,
                "language": self.config_override.language,
                "voice_id": self.config_override.voice_id,
                "rate": self.config_override.rate,
            }
        return payload


@dataclass(frozen=True, slots=True)
class BotHealthResponseDTO:
    """Wire contract for GET /health responses."""

    status: str


@dataclass(frozen=True, slots=True)
class BotErrorResponseDTO:
    """Normalized bot HTTP error payload."""

    success: bool | None = None
    code: str | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class BotVoiceContextResponseDTO:
    """Wire contract for GET /voice-context responses."""

    success: bool
    code: str
    member_id: int | None = None
    guild_id: int | None = None
    guild_name: str | None = None
    channel_id: int | None = None
    channel_name: str | None = None
    message: str | None = None
