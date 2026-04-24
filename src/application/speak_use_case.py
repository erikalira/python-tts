"""Speak-text application use case."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Optional

from src.application.dto import (
    SPEAK_RESULT_MISSING_TEXT,
    SPEAK_RESULT_QUEUE_FULL,
    SPEAK_RESULT_QUEUED,
    SPEAK_RESULT_USER_NOT_IN_CHANNEL,
    SpeakTextInputDTO,
    SpeakTextResult,
)
from src.application.telemetry import BotRuntimeTelemetry, NoOpBotRuntimeTelemetry
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
        queue_runtime_is_active: Callable[[], bool] | None = None,
        telemetry: BotRuntimeTelemetry | None = None,
    ):
        self._channel_repository = channel_repository
        self._audio_queue = audio_queue
        self._max_text_length = max_text_length
        self._voice_channel_resolution = voice_channel_resolution
        self._queue_orchestrator = queue_orchestrator
        self._queue_runtime_is_active = queue_runtime_is_active or (lambda: False)
        self._telemetry = telemetry or NoOpBotRuntimeTelemetry()

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
            self._telemetry.record_submission_result(
                request=domain_request,
                accepted=False,
                code=SPEAK_RESULT_MISSING_TEXT,
                engine=self._resolve_requested_engine(domain_request),
            )
            return SpeakTextResult(success=False, code=SPEAK_RESULT_MISSING_TEXT, queued=False)

        user_channel = await self._channel_repository.find_by_member_id(domain_request.member_id)
        if not user_channel:
            self._telemetry.record_submission_result(
                request=domain_request,
                accepted=False,
                code=SPEAK_RESULT_USER_NOT_IN_CHANNEL,
                engine=self._resolve_requested_engine(domain_request),
            )
            return SpeakTextResult(
                success=False,
                code=SPEAK_RESULT_USER_NOT_IN_CHANNEL,
                queued=False,
            )

        item = AudioQueueItem(request=domain_request, trace_context=getattr(request, "trace_context", None))
        item_id = await self._audio_queue.enqueue(item)
        if item_id is None:
            self._telemetry.record_submission_result(
                request=domain_request,
                accepted=False,
                code=SPEAK_RESULT_QUEUE_FULL,
                engine=self._resolve_requested_engine(domain_request),
            )
            return SpeakTextResult(
                success=False,
                code=SPEAK_RESULT_QUEUE_FULL,
                queued=False,
                error_detail=item.error_message,
            )

        position = await self._audio_queue.get_item_position(item_id)
        guild_id = domain_request.guild_id
        status = await self._audio_queue.get_queue_status(guild_id)
        starts_immediately = (
            position == 0
            and self._queue_runtime_is_active()
            and not await self._audio_queue.is_guild_processing(guild_id)
        )
        self._telemetry.record_submission_result(
            request=domain_request,
            accepted=True,
            code=SPEAK_RESULT_QUEUED,
            engine=self._resolve_requested_engine(domain_request),
        )
        return SpeakTextResult(
            success=True,
            code=SPEAK_RESULT_QUEUED,
            queued=True,
            starts_immediately=starts_immediately,
            position=position,
            queue_size=status.size,
            item_id=item_id,
        )

    def _resolve_requested_engine(self, request: TTSRequest) -> str:
        override = request.config_override
        if override is not None and override.engine:
            return override.engine
        return "configured_default"
