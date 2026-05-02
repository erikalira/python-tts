"""HTTP-specific presentation mapping for typed application results."""

from __future__ import annotations

from dataclasses import asdict

from src.application.dto import (
    SPEAK_RESULT_CROSS_GUILD_CHANNEL,
    SPEAK_RESULT_GENERATION_TIMEOUT,
    SPEAK_RESULT_MISSING_GUILD_ID,
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_OK,
    SPEAK_RESULT_PLAYBACK_TIMEOUT,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_UNKNOWN_ERROR,
    SPEAK_RESULT_USER_LEFT_CHANNEL,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
    SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
    SPEAK_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_VOICE_PERMISSION_DENIED,
    VOICE_CONTEXT_RESULT_MEMBER_REQUIRED,
    VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL,
    BotVoiceContextResponseDTO,
    SpeakTextResult,
    VoiceContextResult,
)
from src.application.rate_limiting import RateLimitResult


class HTTPSpeakPresenter:
    """Map speak results to HTTP text and status."""

    def build_rate_limit_message(self, result: RateLimitResult) -> str:
        retry_after = result.retry_after_seconds
        if retry_after is None:
            return "rate limit exceeded"
        return f"rate limit exceeded; retry after {max(int(retry_after), 1)} seconds"

    def build_message(self, result: SpeakTextResult) -> str:
        if result.code == SPEAK_RESULT_OK:
            return "audio played"
        if result.code == SPEAK_RESULT_QUEUED:
            position = (result.position or 0) + 1
            queue_size = result.queue_size or position
            return f"queued at position {position}/{queue_size}"
        if result.code == SPEAK_RESULT_MISSING_TEXT:
            return "missing text"
        if result.code == SPEAK_RESULT_USER_NOT_IN_CHANNEL:
            return "user is not connected to a voice channel"
        if result.code == SPEAK_RESULT_QUEUE_FULL:
            return "audio queue is full"
        if result.code == SPEAK_RESULT_MISSING_GUILD_ID:
            return "missing guild id"
        if result.code == SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND:
            return "voice channel not found"
        if result.code == SPEAK_RESULT_CROSS_GUILD_CHANNEL:
            return "voice channel belongs to another guild"
        if result.code == SPEAK_RESULT_USER_LEFT_CHANNEL:
            return "user left the voice channel"
        if result.code == SPEAK_RESULT_GENERATION_TIMEOUT:
            return "audio generation timeout"
        if result.code == SPEAK_RESULT_PLAYBACK_TIMEOUT:
            return "playback timeout"
        if result.code == SPEAK_RESULT_VOICE_CONNECTION_FAILED:
            return "failed to connect to voice channel"
        if result.code == SPEAK_RESULT_VOICE_PERMISSION_DENIED:
            return "missing voice permissions"
        if result.code == SPEAK_RESULT_UNKNOWN_ERROR:
            return "playback failed"
        return "unknown speak result"

    def get_status_code(self, result: SpeakTextResult) -> int:
        if result.code in (SPEAK_RESULT_OK, SPEAK_RESULT_QUEUED):
            return 200
        return 400

    def get_rate_limit_status_code(self, result: RateLimitResult) -> int:
        del result
        return 429


class HTTPVoiceContextPresenter:
    """Map voice-context results to HTTP JSON/status."""

    def to_response_dto(self, result: VoiceContextResult) -> BotVoiceContextResponseDTO:
        """Build the explicit HTTP response DTO for voice-context lookups."""
        message = None
        if result.code == VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL:
            message = "user is not connected to a voice channel"
        elif result.code == VOICE_CONTEXT_RESULT_MEMBER_REQUIRED:
            message = "member id is required"

        return BotVoiceContextResponseDTO(
            success=result.success,
            code=result.code,
            member_id=result.member_id,
            guild_id=result.guild_id,
            guild_name=result.guild_name,
            channel_id=result.channel_id,
            channel_name=result.channel_name,
            message=message,
        )

    def to_payload(self, result: VoiceContextResult) -> dict:
        payload = asdict(self.to_response_dto(result))
        return {key: value for key, value in payload.items() if value is not None}

    def get_status_code(self, result: VoiceContextResult) -> int:
        if result.code == VOICE_CONTEXT_RESULT_MEMBER_REQUIRED:
            return 400
        if result.code == VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL:
            return 404
        return 200
