"""Queue draining and playback orchestration for shared TTS flows."""

from __future__ import annotations

import asyncio
import logging
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

        try:
            if not request.guild_id:
                error = "Guild ID nao foi fornecido - isolamento de servidor falhou"
                item.mark_failed(error)
                await self._audio_queue.update_item(item)
                return SpeakTextResult(
                    success=False,
                    code=SPEAK_RESULT_MISSING_GUILD_ID,
                    queued=True,
                    item_id=item.item_id,
                    error_detail=error,
                )

            resolution = await self._voice_channel_resolution.resolve_for_request(request)
            if not resolution:
                error = "Bot nao conseguiu encontrar sua sala de voz"
                item.mark_failed(error)
                await self._audio_queue.update_item(item)
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
                return SpeakTextResult(
                    success=False,
                    code=SPEAK_RESULT_CROSS_GUILD_CHANNEL,
                    queued=True,
                    item_id=item.item_id,
                    error_detail=error,
                )

            config = await self._config_repository.load_config_async(request.guild_id, user_id=request.member_id)
            config = self._apply_request_override(config, request.config_override)
            try:
                audio = await asyncio.wait_for(
                    self._tts_engine.generate_audio(request.text, config),
                    timeout=self._generation_timeout_seconds,
                )
            except asyncio.TimeoutError:
                error = "Tempo limite excedido durante geracao do audio"
                item.mark_failed(error)
                await self._audio_queue.update_item(item)
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

            if not voice_channel.is_connected():
                await voice_channel.connect()

            if request.member_id and not await self._voice_channel_resolution.is_member_in_channel(
                request.member_id, voice_channel
            ):
                error = "Voce saiu do canal de voz"
                item.mark_failed(error)
                await self._audio_queue.update_item(item)
                return SpeakTextResult(
                    success=False,
                    code=SPEAK_RESULT_USER_LEFT_CHANNEL,
                    queued=True,
                    item_id=item.item_id,
                    error_detail=error,
                )

            try:
                await asyncio.wait_for(voice_channel.play_audio(audio), timeout=self._playback_timeout_seconds)
                item.mark_completed()
                await self._audio_queue.update_item(item)
                self._telemetry.record_processing_result(
                    item=item,
                    success=True,
                    code=SPEAK_RESULT_OK,
                    engine=config.engine,
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
                self._telemetry.record_processing_result(
                    item=item,
                    success=False,
                    code=SPEAK_RESULT_PLAYBACK_TIMEOUT,
                    engine=config.engine,
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

    def _resolve_engine_name(self, item: AudioQueueItem) -> str:
        override = item.request.config_override
        if override is not None and override.engine:
            return override.engine
        return "configured_default"
