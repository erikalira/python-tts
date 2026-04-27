"""Discord-specific presentation mapping for typed application results."""

from __future__ import annotations

from src.application.dto import (
    JOIN_RESULT_MISSING_GUILD_ID,
    JOIN_RESULT_OK,
    JOIN_RESULT_USER_NOT_IN_CHANNEL,
    JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND,
    JOIN_RESULT_VOICE_CONNECTION_FAILED,
    LEAVE_RESULT_MISSING_GUILD_ID,
    LEAVE_RESULT_NOT_CONNECTED,
    LEAVE_RESULT_OK,
    LEAVE_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_CROSS_GUILD_CHANNEL,
    SPEAK_RESULT_GENERATION_TIMEOUT,
    SPEAK_RESULT_MISSING_GUILD_ID,
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_PLAYBACK_TIMEOUT,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_UNKNOWN_ERROR,
    SPEAK_RESULT_USER_LEFT_CHANNEL,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
    SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
    SPEAK_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_VOICE_PERMISSION_DENIED,
    JoinVoiceChannelResult,
    LeaveVoiceChannelResult,
    SpeakTextResult,
)
from src.application.rate_limiting import RateLimitResult
from src.presentation.discord_i18n import DEFAULT_LOCALE, DiscordMessageCatalog


_MESSAGES = DiscordMessageCatalog()


class DiscordSpeakPresenter:
    """Map speak results to Discord-facing messages."""

    def build_rate_limit_message(self, result: RateLimitResult, locale: str = DEFAULT_LOCALE) -> str:
        retry_after = result.retry_after_seconds
        if retry_after is None:
            return _MESSAGES.text("rate_limit.without_retry", locale)
        return _MESSAGES.text("rate_limit.with_retry", locale, seconds=max(int(retry_after), 1))

    def build_message(self, result: SpeakTextResult, locale: str = DEFAULT_LOCALE) -> str:
        code = result.code
        if code == SPEAK_RESULT_QUEUED:
            position = (result.position or 0) + 1
            queue_size = result.queue_size or position
            return _MESSAGES.text("speak.queued", locale, position=position, queue_size=queue_size)
        if code == SPEAK_RESULT_MISSING_TEXT:
            return _MESSAGES.text("speak.missing_text", locale)
        if code == SPEAK_RESULT_USER_NOT_IN_CHANNEL:
            return _MESSAGES.text("speak.user_not_in_channel", locale)
        if code == SPEAK_RESULT_QUEUE_FULL:
            return _MESSAGES.text("speak.queue_full", locale)
        if code == SPEAK_RESULT_MISSING_GUILD_ID:
            return _MESSAGES.text("speak.missing_guild_id", locale)
        if code == SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND:
            return _MESSAGES.text("speak.voice_channel_not_found", locale)
        if code == SPEAK_RESULT_CROSS_GUILD_CHANNEL:
            return _MESSAGES.text("speak.cross_guild_channel", locale)
        if code == SPEAK_RESULT_USER_LEFT_CHANNEL:
            return _MESSAGES.text("speak.user_left_channel", locale)
        if code == SPEAK_RESULT_GENERATION_TIMEOUT:
            return _MESSAGES.text("speak.generation_timeout", locale)
        if code == SPEAK_RESULT_PLAYBACK_TIMEOUT:
            return _MESSAGES.text("speak.playback_timeout", locale)
        if code == SPEAK_RESULT_VOICE_CONNECTION_FAILED:
            return _MESSAGES.text("speak.voice_connection_failed", locale)
        if code == SPEAK_RESULT_VOICE_PERMISSION_DENIED:
            return _MESSAGES.text("speak.voice_permission_denied", locale)
        if code == SPEAK_RESULT_UNKNOWN_ERROR:
            return _MESSAGES.text("speak.unknown_error", locale)
        return _MESSAGES.text("speak.unexpected_error", locale)


class DiscordJoinPresenter:
    """Map join results to Discord messages."""

    def build_message(self, result: JoinVoiceChannelResult, locale: str = DEFAULT_LOCALE) -> str:
        if result.code == JOIN_RESULT_OK:
            return _MESSAGES.text("join.ok", locale)
        if result.code == JOIN_RESULT_USER_NOT_IN_CHANNEL:
            return _MESSAGES.text("join.user_not_in_channel", locale)
        if result.code == JOIN_RESULT_MISSING_GUILD_ID:
            return _MESSAGES.text("join.missing_guild_id", locale)
        if result.code == JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND:
            return _MESSAGES.text("join.voice_channel_not_found", locale)
        if result.code == JOIN_RESULT_VOICE_CONNECTION_FAILED:
            return _MESSAGES.text("join.voice_connection_failed", locale)
        return _MESSAGES.text("join.voice_connection_failed", locale)


class DiscordLeavePresenter:
    """Map leave results to Discord messages."""

    def build_message(self, result: LeaveVoiceChannelResult, locale: str = DEFAULT_LOCALE) -> str:
        if result.code == LEAVE_RESULT_OK:
            return _MESSAGES.text("leave.ok", locale)
        if result.code == LEAVE_RESULT_NOT_CONNECTED:
            return _MESSAGES.text("leave.not_connected", locale)
        if result.code == LEAVE_RESULT_MISSING_GUILD_ID:
            return _MESSAGES.text("leave.missing_guild_id", locale)
        if result.code == LEAVE_RESULT_VOICE_CONNECTION_FAILED and result.error_detail:
            return _MESSAGES.text("leave.voice_connection_failed", locale, error_detail=result.error_detail)
        return _MESSAGES.text("leave.error", locale)
