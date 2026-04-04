"""Application layer use cases and result code compatibility exports."""

from __future__ import annotations

import logging
from typing import Optional

from src.application.results import (
    JOIN_RESULT_MISSING_GUILD_ID,
    JOIN_RESULT_OK,
    JOIN_RESULT_USER_NOT_IN_CHANNEL,
    JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND,
    JOIN_RESULT_VOICE_CONNECTION_FAILED,
    LEAVE_RESULT_MISSING_GUILD_ID,
    LEAVE_RESULT_NOT_CONNECTED,
    LEAVE_RESULT_OK,
    LEAVE_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_OK,
    SPEAK_RESULT_PLAYBACK_TIMEOUT,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_UNKNOWN_ERROR,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
    SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
    SPEAK_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_VOICE_PERMISSION_DENIED,
    VOICE_CONTEXT_RESULT_MEMBER_REQUIRED,
    VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL,
    VOICE_CONTEXT_RESULT_OK,
    JoinVoiceChannelResult,
    LeaveVoiceChannelResult,
    SpeakTextResult,
    VoiceContextResult,
)
from src.application.tts_queue_orchestrator import TTSQueueOrchestrator
from src.application.tts_text import prepare_tts_text
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.core.entities import AudioQueueItem, TTSRequest
from src.core.interfaces import IAudioQueue, IConfigRepository, IVoiceChannelRepository

logger = logging.getLogger(__name__)


class JoinVoiceChannelUseCase:
    """Use case for connecting the bot to a member's current voice channel."""

    def __init__(self, channel_repository: IVoiceChannelRepository):
        self._channel_repository = channel_repository

    async def execute(self, guild_id: Optional[int], member_id: Optional[int]) -> JoinVoiceChannelResult:
        if guild_id is None:
            return JoinVoiceChannelResult(success=False, code=JOIN_RESULT_MISSING_GUILD_ID)
        if member_id is None:
            return JoinVoiceChannelResult(success=False, code=JOIN_RESULT_USER_NOT_IN_CHANNEL)

        channel = await self._channel_repository.find_by_member_id(member_id)
        if not channel:
            return JoinVoiceChannelResult(success=False, code=JOIN_RESULT_USER_NOT_IN_CHANNEL)
        if channel.get_guild_id() != guild_id:
            return JoinVoiceChannelResult(success=False, code=JOIN_RESULT_VOICE_CHANNEL_NOT_FOUND)

        try:
            await channel.connect()
        except Exception as exc:
            logger.error("[JOIN_USE_CASE] Failed to connect to voice channel: %s", exc, exc_info=True)
            return JoinVoiceChannelResult(
                success=False,
                code=JOIN_RESULT_VOICE_CONNECTION_FAILED,
                error_detail=str(exc),
            )

        return JoinVoiceChannelResult(success=True, code=JOIN_RESULT_OK)


class LeaveVoiceChannelUseCase:
    """Use case for disconnecting the bot from a guild voice channel."""

    def __init__(self, channel_repository: IVoiceChannelRepository):
        self._channel_repository = channel_repository

    async def execute(self, guild_id: Optional[int]) -> LeaveVoiceChannelResult:
        if guild_id is None:
            return LeaveVoiceChannelResult(success=False, code=LEAVE_RESULT_MISSING_GUILD_ID)

        channel = await self._channel_repository.find_by_guild_id(guild_id)
        if not channel or not channel.is_connected():
            return LeaveVoiceChannelResult(success=False, code=LEAVE_RESULT_NOT_CONNECTED)

        try:
            await channel.disconnect()
        except Exception as exc:
            logger.error("[LEAVE_USE_CASE] Failed to disconnect from voice channel: %s", exc, exc_info=True)
            return LeaveVoiceChannelResult(
                success=False,
                code=LEAVE_RESULT_VOICE_CONNECTION_FAILED,
                error_detail=str(exc),
            )

        return LeaveVoiceChannelResult(success=True, code=LEAVE_RESULT_OK)


class GetCurrentVoiceContextUseCase:
    """Use case for discovering the member's current voice context."""

    def __init__(self, channel_repository: IVoiceChannelRepository):
        self._channel_repository = channel_repository

    async def execute(self, member_id: Optional[int]) -> VoiceContextResult:
        if member_id is None:
            return VoiceContextResult(success=False, code=VOICE_CONTEXT_RESULT_MEMBER_REQUIRED)

        channel = await self._channel_repository.find_by_member_id(member_id)
        if not channel:
            return VoiceContextResult(success=False, code=VOICE_CONTEXT_RESULT_NOT_IN_CHANNEL)

        return VoiceContextResult(
            success=True,
            code=VOICE_CONTEXT_RESULT_OK,
            member_id=member_id,
            guild_id=channel.get_guild_id(),
            guild_name=channel.get_guild_name(),
            channel_id=channel.get_channel_id(),
            channel_name=channel.get_channel_name(),
        )


class SpeakTextUseCase:
    """Use case for accepting TTS requests and delegating queued playback."""

    def __init__(
        self,
        channel_repository: IVoiceChannelRepository,
        audio_queue: IAudioQueue,
        voice_channel_resolution: VoiceChannelResolutionService,
        queue_orchestrator: TTSQueueOrchestrator,
        max_text_length: Optional[int] = None,
    ):
        self._channel_repository = channel_repository
        self._audio_queue = audio_queue
        self._max_text_length = max_text_length
        self._voice_channel_resolution = voice_channel_resolution
        self._queue_orchestrator = queue_orchestrator

    async def execute(self, request: TTSRequest) -> SpeakTextResult:
        prepared_text = prepare_tts_text(request.text, self._max_text_length)
        inferred_guild_id = await self._voice_channel_resolution.infer_guild_id(request)
        request = TTSRequest(
            text=prepared_text,
            channel_id=request.channel_id,
            guild_id=inferred_guild_id,
            member_id=request.member_id,
        )

        logger.info(
            "[USE_CASE] Speak request from user %s: text='%s...', guild_id=%s",
            request.member_id,
            request.text[:50],
            request.guild_id,
        )

        if not request.text:
            return SpeakTextResult(success=False, code=SPEAK_RESULT_MISSING_TEXT, queued=False)

        user_channel = await self._channel_repository.find_by_member_id(request.member_id)
        if not user_channel:
            return SpeakTextResult(
                success=False,
                code=SPEAK_RESULT_USER_NOT_IN_CHANNEL,
                queued=False,
            )

        item = AudioQueueItem(request=request)
        item_id = await self._audio_queue.enqueue(item)
        if item_id is None:
            return SpeakTextResult(
                success=False,
                code=SPEAK_RESULT_QUEUE_FULL,
                queued=False,
                error_detail=item.error_message,
            )

        position = await self._audio_queue.get_item_position(item_id)
        guild_id = request.guild_id
        if position == 0 and not self._queue_orchestrator.is_processing(guild_id):
            return await self._queue_orchestrator.start_processing_for_item(guild_id)

        status = await self._audio_queue.get_queue_status(guild_id)
        return SpeakTextResult(
            success=True,
            code=SPEAK_RESULT_QUEUED,
            queued=True,
            position=position,
            queue_size=status["size"],
            item_id=item_id,
        )


class ConfigureTTSUseCase:
    """Use case for configuring TTS settings per guild."""

    def __init__(self, config_repository: IConfigRepository):
        self._config_repository = config_repository

    def get_config(self, guild_id: int) -> dict:
        if guild_id is None:
            return {"success": False, "message": "Guild ID is required"}

        config = self._config_repository.get_config(guild_id)
        return {
            "success": True,
            "guild_id": guild_id,
            "config": {
                "engine": config.engine,
                "language": config.language,
                "voice_id": config.voice_id,
                "rate": config.rate,
            },
        }

    async def update_config_async(
        self,
        guild_id: int,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        voice_id: Optional[str] = None,
        rate: Optional[int] = None,
    ) -> dict:
        if guild_id is None:
            return {"success": False, "message": "Guild ID is required"}

        logger.info("[CONFIG_USE_CASE] Updating config for guild %s", guild_id)
        current_config = self._config_repository.get_config(guild_id)

        if engine is not None:
            if engine.lower() not in ["gtts", "pyttsx3"]:
                return {"success": False, "message": "Invalid engine. Use 'gtts' or 'pyttsx3'"}
            current_config.engine = engine.lower()
        if language is not None:
            current_config.language = language.lower()
        if voice_id is not None:
            current_config.voice_id = voice_id
        if rate is not None:
            if not (50 <= rate <= 300):
                return {"success": False, "message": "Rate must be between 50 and 300"}
            current_config.rate = rate

        saved = await self._config_repository.save_config_async(guild_id, current_config)
        if not saved:
            logger.error("[CONFIG_USE_CASE] Failed to persist config for guild %s", guild_id)
            return {"success": False, "message": "Failed to save configuration"}

        return {
            "success": True,
            "guild_id": guild_id,
            "config": {
                "engine": current_config.engine,
                "language": current_config.language,
                "voice_id": current_config.voice_id,
                "rate": current_config.rate,
            },
        }
