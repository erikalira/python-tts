"""Speak-text application use case."""

from __future__ import annotations

import logging
from typing import Optional

from src.application.dto import (
    SpeakTextResult,
    SpeakTextInputDTO,
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
)
from src.application.tts_queue_orchestrator import TTSQueueOrchestrator
from src.application.tts_text import prepare_tts_text
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.core.entities import AudioQueueItem, TTSRequest
from src.core.interfaces import IAudioQueue, IVoiceChannelRepository

logger = logging.getLogger(__name__)


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

    async def execute(self, request: SpeakTextInputDTO) -> SpeakTextResult:
        prepared_text = prepare_tts_text(request.text, self._max_text_length)
        domain_request = TTSRequest(
            text=prepared_text,
            channel_id=request.channel_id,
            guild_id=request.guild_id,
            member_id=request.member_id,
            config_override=request.config_override,
        )
        inferred_guild_id = await self._voice_channel_resolution.infer_guild_id(domain_request)
        domain_request = TTSRequest(
            text=prepared_text,
            channel_id=request.channel_id,
            guild_id=inferred_guild_id,
            member_id=request.member_id,
            config_override=request.config_override,
        )

        logger.info(
            "[USE_CASE] Speak request from user %s: text='%s...', guild_id=%s",
            domain_request.member_id,
            domain_request.text[:50],
            domain_request.guild_id,
        )

        if not domain_request.text:
            return SpeakTextResult(success=False, code=SPEAK_RESULT_MISSING_TEXT, queued=False)

        user_channel = await self._channel_repository.find_by_member_id(domain_request.member_id)
        if not user_channel:
            return SpeakTextResult(
                success=False,
                code=SPEAK_RESULT_USER_NOT_IN_CHANNEL,
                queued=False,
            )

        item = AudioQueueItem(request=domain_request)
        item_id = await self._audio_queue.enqueue(item)
        if item_id is None:
            return SpeakTextResult(
                success=False,
                code=SPEAK_RESULT_QUEUE_FULL,
                queued=False,
                error_detail=item.error_message,
            )

        position = await self._audio_queue.get_item_position(item_id)
        guild_id = domain_request.guild_id
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
