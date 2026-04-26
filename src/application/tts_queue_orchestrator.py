"""Queue draining and playback orchestration for shared TTS flows."""

from __future__ import annotations

import asyncio
import logging
import time
from typing import Optional

from src.application.dto import (
    SPEAK_RESULT_CROSS_GUILD_CHANNEL,
    SPEAK_RESULT_GENERATION_TIMEOUT,
    SPEAK_RESULT_MISSING_GUILD_ID,
    SPEAK_RESULT_OK,
    SPEAK_RESULT_PLAYBACK_TIMEOUT,
    SPEAK_RESULT_UNKNOWN_ERROR,
    SPEAK_RESULT_USER_LEFT_CHANNEL,
    SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
    SPEAK_RESULT_VOICE_CONNECTION_FAILED,
    SPEAK_RESULT_VOICE_PERMISSION_DENIED,
    SpeakTextResult,
)
from src.application.runtime_telemetry import NullRuntimeSpanContext, RuntimeSpan, RuntimeTelemetry
from src.application.telemetry import BotRuntimeTelemetry, NoOpBotRuntimeTelemetry
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.core.entities import AudioQueueItem, TTSConfig
from src.core.interfaces import IAudioFileCleanup, IAudioQueue, IConfigRepository, ITTSEngine
from src.core.timeouts import (
    DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS,
    DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS,
)

logger = logging.getLogger(__name__)


class TTSQueueOrchestrator:
    """Coordinate queue draining and playback per guild."""

    def __init__(
        self,
        *,
        tts_engine: ITTSEngine,
        config_repository: IConfigRepository,
        audio_queue: IAudioQueue,
        voice_channel_resolution: VoiceChannelResolutionService,
        audio_cleanup: IAudioFileCleanup,
        generation_timeout_seconds: float = DEFAULT_BOT_TTS_GENERATION_TIMEOUT_SECONDS,
        playback_timeout_seconds: float = DEFAULT_BOT_TTS_PLAYBACK_TIMEOUT_SECONDS,
        telemetry: BotRuntimeTelemetry | None = None,
        otel_runtime: RuntimeTelemetry | None = None,
    ):
        self._tts_engine = tts_engine
        self._config_repository = config_repository
        self._audio_queue = audio_queue
        self._voice_channel_resolution = voice_channel_resolution
        self._audio_cleanup = audio_cleanup
        self._generation_timeout_seconds = generation_timeout_seconds
        self._playback_timeout_seconds = playback_timeout_seconds
        self._processing_guilds: set[Optional[int]] = set()
        self._telemetry = telemetry or NoOpBotRuntimeTelemetry()
        self._otel_runtime = otel_runtime

    def is_processing(self, guild_id: Optional[int]) -> bool:
        return guild_id in self._processing_guilds

    async def start_processing_for_item(self, guild_id: Optional[int]) -> SpeakTextResult:
        self._processing_guilds.add(guild_id)
        try:
            item = await self._audio_queue.dequeue(guild_id)
            if item is None:
                self._clear_guild_processing(guild_id)
                return SpeakTextResult(
                    success=False,
                    code=SPEAK_RESULT_UNKNOWN_ERROR,
                    queued=False,
                    error_detail="Queue item disappeared before processing",
                )

            result = await self._process_item(item)
            self._clear_guild_processing(guild_id)
            return result
        except Exception:
            self._clear_guild_processing(guild_id)
            raise

    def _clear_guild_processing(self, guild_id: Optional[int]) -> None:
        self._processing_guilds.discard(guild_id)

    async def _process_item(self, item: AudioQueueItem) -> SpeakTextResult:
        item.mark_processing()
        await self._audio_queue.update_item(item)
        request = item.request
        audio = None
        processing_started_at = time.perf_counter()

        with self._otel_runtime.start_internal_span(
            "tts_queue.process_item",
            attributes={
                "guild_id": str(request.guild_id) if request.guild_id is not None else "unknown",
                "engine": self._resolve_engine_name(item),
            },
        ) if self._otel_runtime is not None else NullRuntimeSpanContext() as processing_span:
            try:
                if not request.guild_id:
                    error = "Guild ID nao foi fornecido - isolamento de servidor falhou"
                    item.mark_failed(error)
                    await self._audio_queue.update_item(item)
                    self._record_failed_queue_item(
                        item=item,
                        code=SPEAK_RESULT_MISSING_GUILD_ID,
                        processing_span=processing_span,
                    )
                    return SpeakTextResult(
                        success=False,
                        code=SPEAK_RESULT_MISSING_GUILD_ID,
                        queued=True,
                        item_id=item.item_id,
                        error_detail=error,
                    )

                resolution_started_at = time.perf_counter()
                resolution = await self._voice_channel_resolution.resolve_for_request(request)
                resolution_ms = (time.perf_counter() - resolution_started_at) * 1000
                if not resolution:
                    error = "Bot nao conseguiu encontrar sua sala de voz"
                    item.mark_failed(error)
                    await self._audio_queue.update_item(item)
                    self._record_failed_queue_item(
                        item=item,
                        code=SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
                        processing_span=processing_span,
                    )
                    return SpeakTextResult(
                        success=False,
                        code=SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
                        queued=True,
                        item_id=item.item_id,
                        error_detail=error,
                    )

                voice_channel = resolution.channel
                channel_guild_id = voice_channel.get_guild_id()
                if channel_guild_id != request.guild_id:
                    error = "Canal de voz pertence a servidor diferente"
                    item.mark_failed(error)
                    await self._audio_queue.update_item(item)
                    self._record_failed_queue_item(
                        item=item,
                        code=SPEAK_RESULT_CROSS_GUILD_CHANNEL,
                        processing_span=processing_span,
                    )
                    return SpeakTextResult(
                        success=False,
                        code=SPEAK_RESULT_CROSS_GUILD_CHANNEL,
                        queued=True,
                        item_id=item.item_id,
                        error_detail=error,
                    )

                config_started_at = time.perf_counter()
                config = await self._config_repository.load_config_async(request.guild_id, user_id=request.member_id)
                config_load_ms = (time.perf_counter() - config_started_at) * 1000
                config = self._apply_request_override(config, request.config_override)
                telemetry_engine = self._resolve_engine_name(item)
                try:
                    generation_started_at = time.perf_counter()
                    with self._otel_runtime.start_internal_span(
                        "tts_engine.generate_audio",
                        attributes={"guild_id": str(request.guild_id), "engine": config.engine},
                    ) if self._otel_runtime is not None else NullRuntimeSpanContext() as generate_span:
                        audio = await asyncio.wait_for(
                            self._tts_engine.generate_audio(request.text, config),
                            timeout=self._generation_timeout_seconds,
                        )
                        generate_span.set_attribute("result_code", "ok")
                    generation_ms = (time.perf_counter() - generation_started_at) * 1000
                except asyncio.TimeoutError:
                    error = "Tempo limite excedido durante geracao do audio"
                    item.mark_failed(error)
                    await self._audio_queue.update_item(item)
                    processing_span.set_attribute("result_code", SPEAK_RESULT_GENERATION_TIMEOUT)
                    processing_span.set_attribute("timeout_flag", True)
                    self._telemetry.record_processing_result(
                        item=item,
                        success=False,
                        code=SPEAK_RESULT_GENERATION_TIMEOUT,
                        engine=telemetry_engine,
                    )
                    if self._otel_runtime is not None:
                        self._otel_runtime.record_queue_item_processed(
                            guild_id=request.guild_id,
                            engine=config.engine,
                            result_code=SPEAK_RESULT_GENERATION_TIMEOUT,
                            success=False,
                            timeout_flag=True,
                        )
                    logger.warning(
                        "[QUEUE_ORCHESTRATOR] Audio generation timed out for item %s after %ss",
                        item.item_id,
                        self._generation_timeout_seconds,
                    )
                    return SpeakTextResult(
                        success=False,
                        code=SPEAK_RESULT_GENERATION_TIMEOUT,
                        queued=True,
                        item_id=item.item_id,
                        error_detail=error,
                    )

                connect_ms = 0.0
                if not voice_channel.is_connected():
                    connect_started_at = time.perf_counter()
                    await voice_channel.connect()
                    connect_ms = (time.perf_counter() - connect_started_at) * 1000

                member_validation_started_at = time.perf_counter()
                if request.member_id and not await self._voice_channel_resolution.is_member_in_channel(
                    request.member_id, voice_channel
                ):
                    error = "Voce saiu do canal de voz"
                    item.mark_failed(error)
                    await self._audio_queue.update_item(item)
                    self._record_failed_queue_item(
                        item=item,
                        code=SPEAK_RESULT_USER_LEFT_CHANNEL,
                        processing_span=processing_span,
                    )
                    return SpeakTextResult(
                        success=False,
                        code=SPEAK_RESULT_USER_LEFT_CHANNEL,
                        queued=True,
                        item_id=item.item_id,
                        error_detail=error,
                    )
                member_validation_ms = (time.perf_counter() - member_validation_started_at) * 1000

                try:
                    playback_started_at = time.perf_counter()
                    with self._otel_runtime.start_internal_span(
                        "tts_engine.play_audio",
                        attributes={"guild_id": str(request.guild_id), "engine": config.engine},
                    ) if self._otel_runtime is not None else NullRuntimeSpanContext() as playback_span:
                        await asyncio.wait_for(voice_channel.play_audio(audio), timeout=self._playback_timeout_seconds)
                        playback_span.set_attribute("result_code", "ok")
                    item.mark_completed()
                    await self._audio_queue.update_item(item)
                    playback_ms = (time.perf_counter() - playback_started_at) * 1000
                    total_processing_ms = (time.perf_counter() - processing_started_at) * 1000
                    logger.info(
                        "[QUEUE_ORCHESTRATOR] Item %s processed | guild_id=%s | engine=%s | resolution_ms=%.2f | config_load_ms=%.2f | generation_ms=%.2f | connect_ms=%.2f | member_validation_ms=%.2f | playback_ms=%.2f | total_processing_ms=%.2f",
                        item.item_id,
                        request.guild_id,
                        config.engine,
                        resolution_ms,
                        config_load_ms,
                        generation_ms,
                        connect_ms,
                        member_validation_ms,
                        playback_ms,
                        total_processing_ms,
                    )
                    processing_span.set_attribute("result_code", SPEAK_RESULT_OK)
                    processing_span.set_attribute("timeout_flag", False)
                    self._telemetry.record_processing_result(
                        item=item,
                        success=True,
                        code=SPEAK_RESULT_OK,
                        engine=telemetry_engine,
                    )
                    if self._otel_runtime is not None:
                        self._otel_runtime.record_queue_item_processed(
                            guild_id=request.guild_id,
                            engine=config.engine,
                            result_code=SPEAK_RESULT_OK,
                            success=True,
                            timeout_flag=False,
                        )
                    return SpeakTextResult(
                        success=True,
                        code=SPEAK_RESULT_OK,
                        queued=False,
                        item_id=item.item_id,
                    )
                except asyncio.TimeoutError:
                    error = "Tempo limite excedido durante reproducao"
                    item.mark_failed(error)
                    await self._audio_queue.update_item(item)
                    processing_span.set_attribute("result_code", SPEAK_RESULT_PLAYBACK_TIMEOUT)
                    processing_span.set_attribute("timeout_flag", True)
                    self._telemetry.record_processing_result(
                        item=item,
                        success=False,
                        code=SPEAK_RESULT_PLAYBACK_TIMEOUT,
                        engine=telemetry_engine,
                    )
                    if self._otel_runtime is not None:
                        self._otel_runtime.record_queue_item_processed(
                            guild_id=request.guild_id,
                            engine=config.engine,
                            result_code=SPEAK_RESULT_PLAYBACK_TIMEOUT,
                            success=False,
                            timeout_flag=True,
                        )
                    logger.warning(
                        "[QUEUE_ORCHESTRATOR] Audio playback timed out for item %s after %ss",
                        item.item_id,
                        self._playback_timeout_seconds,
                    )
                    return SpeakTextResult(
                        success=False,
                        code=SPEAK_RESULT_PLAYBACK_TIMEOUT,
                        queued=True,
                        item_id=item.item_id,
                        error_detail=error,
                    )
            except Exception as exc:
                error_msg = str(exc)
                item.mark_failed(error_msg)
                await self._audio_queue.update_item(item)

                error_lower = error_msg.lower()
                if "4017" in error_lower or "dave" in error_lower:
                    code = SPEAK_RESULT_VOICE_CONNECTION_FAILED
                elif "not connected" in error_lower or "connection" in error_lower:
                    code = SPEAK_RESULT_VOICE_CONNECTION_FAILED
                elif "permission" in error_lower:
                    code = SPEAK_RESULT_VOICE_PERMISSION_DENIED
                else:
                    code = SPEAK_RESULT_UNKNOWN_ERROR

                self._telemetry.record_processing_result(
                    item=item,
                    success=False,
                    code=code,
                    engine=self._resolve_engine_name(item),
                )
                processing_span.set_attribute("result_code", code)
                processing_span.set_attribute(
                    "timeout_flag",
                    code in {SPEAK_RESULT_GENERATION_TIMEOUT, SPEAK_RESULT_PLAYBACK_TIMEOUT},
                )
                if self._otel_runtime is not None:
                    self._otel_runtime.mark_span_error(processing_span, exc)
                    self._otel_runtime.record_queue_item_processed(
                        guild_id=request.guild_id,
                        engine=self._resolve_engine_name(item),
                        result_code=code,
                        success=False,
                        timeout_flag=code in {SPEAK_RESULT_GENERATION_TIMEOUT, SPEAK_RESULT_PLAYBACK_TIMEOUT},
                    )
                return SpeakTextResult(
                    success=False,
                    code=code,
                    queued=True,
                    item_id=item.item_id,
                    error_detail=error_msg,
                )
            finally:
                if audio:
                    try:
                        await self._audio_cleanup.cleanup(audio)
                    except Exception as cleanup_error:
                        logger.warning(
                            "[QUEUE_ORCHESTRATOR] Error cleaning up audio file %s: %s",
                            audio.path,
                            cleanup_error,
                        )

    def _apply_request_override(self, base_config: TTSConfig, override: TTSConfig | None) -> TTSConfig:
        if override is None:
            return base_config

        return TTSConfig(
            engine=override.engine,
            language=override.language,
            voice_id=override.voice_id,
            rate=override.rate,
            output_device=base_config.output_device,
        )

    def _record_failed_queue_item(
        self,
        *,
        item: AudioQueueItem,
        code: str,
        processing_span: RuntimeSpan,
    ) -> None:
        engine = self._resolve_engine_name(item)
        processing_span.set_attribute("result_code", code)
        processing_span.set_attribute(
            "timeout_flag",
            code in {SPEAK_RESULT_GENERATION_TIMEOUT, SPEAK_RESULT_PLAYBACK_TIMEOUT},
        )
        self._telemetry.record_processing_result(
            item=item,
            success=False,
            code=code,
            engine=engine,
        )
        if self._otel_runtime is not None:
            self._otel_runtime.record_queue_item_processed(
                guild_id=item.request.guild_id,
                engine=engine,
                result_code=code,
                success=False,
                timeout_flag=code in {SPEAK_RESULT_GENERATION_TIMEOUT, SPEAK_RESULT_PLAYBACK_TIMEOUT},
            )

    def _resolve_engine_name(self, item: AudioQueueItem) -> str:
        override = item.request.config_override
        if override is not None and override.engine:
            return override.engine
        return "configured_default"
