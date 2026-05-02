"""Typed application result objects for shared TTS flows."""

from __future__ import annotations

from dataclasses import dataclass

SPEAK_RESULT_OK = "ok"
SPEAK_RESULT_QUEUED = "queued"
SPEAK_RESULT_MISSING_TEXT = "missing_text"
SPEAK_RESULT_USER_NOT_IN_CHANNEL = "user_not_in_channel"
SPEAK_RESULT_QUEUE_FULL = "queue_full"
SPEAK_RESULT_MISSING_GUILD_ID = "missing_guild_id"
SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND = "voice_channel_not_found"
SPEAK_RESULT_CROSS_GUILD_CHANNEL = "cross_guild_channel"
SPEAK_RESULT_USER_LEFT_CHANNEL = "user_left_channel"
SPEAK_RESULT_GENERATION_TIMEOUT = "generation_timeout"
SPEAK_RESULT_PLAYBACK_TIMEOUT = "playback_timeout"
SPEAK_RESULT_VOICE_CONNECTION_FAILED = "voice_connection_failed"
SPEAK_RESULT_VOICE_PERMISSION_DENIED = "voice_permission_denied"
SPEAK_RESULT_UNKNOWN_ERROR = "unknown_error"

JOIN_RESULT_OK = "ok"
JOIN_RESULT_MISSING_GUILD_ID = "missing_guild_id"
JOIN_RESULT_USER_NOT_IN_CHANNEL = "user_not_in_channel"
JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND = "voice_channel_not_found"
JOIN_RESULT_VOICE_CONNECTION_FAILED = "voice_connection_failed"

LEAVE_RESULT_OK = "ok"
LEAVE_RESULT_MISSING_GUILD_ID = "missing_guild_id"
LEAVE_RESULT_NOT_CONNECTED = "not_connected"
LEAVE_RESULT_VOICE_CONNECTION_FAILED = "voice_connection_failed"

VOICE_CONTEXT_RESULT_OK = "ok"
VOICE_CONTEXT_RESULT_MEMBER_REQUIRED = "member_required"
VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL = "not_in_channel"


@dataclass(slots=True)
class ResultBase:
    """Typed result base for shared application flows."""


@dataclass(slots=True)
class JoinVoiceChannelResult(ResultBase):
    success: bool
    code: str
    error_detail: str | None = None


@dataclass(slots=True)
class LeaveVoiceChannelResult(ResultBase):
    success: bool
    code: str
    error_detail: str | None = None


@dataclass(slots=True)
class VoiceContextResult(ResultBase):
    success: bool
    code: str
    member_id: int | None = None
    guild_id: int | None = None
    guild_name: str | None = None
    channel_id: int | None = None
    channel_name: str | None = None


@dataclass(slots=True)
class SpeakTextResult(ResultBase):
    success: bool
    code: str
    queued: bool
    starts_immediately: bool = False
    position: int | None = None
    queue_size: int | None = None
    item_id: str | None = None
    error_detail: str | None = None


@dataclass(slots=True)
class TTSConfigurationData(ResultBase):
    engine: str
    language: str
    voice_id: str
    rate: int


@dataclass(slots=True)
class ConfigureTTSResult(ResultBase):
    success: bool
    guild_id: int | None = None
    config: TTSConfigurationData | None = None
    message: str | None = None
    scope: str | None = None
