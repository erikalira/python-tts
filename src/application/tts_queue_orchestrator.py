"""Queue draining and playback orchestration for shared TTS flows."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from src.application.dto import (
    SPEAK_RESULT_CROSS_GUILD_CHANNEL,
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
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.core.entities import AudioQueueItem, TTSConfig
from src.core.interfaces import IAudioFileCleanup, IAudioQueue, IConfigRepository, ITTSEngine

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
    ):
        self._tts_engine = tts_engine
        self._config_repository = config_repository
        self._audio_queue = audio_queue
        self._voice_channel_resolution = voice_channel_resolution
        self._audio_cleanup = audio_cleanup
        self._guild_processors: dict[Optional[int], asyncio.Task] = {}
        self._processing_guilds: set[Optional[int]] = set()

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
            self._ensure_guild_processor(guild_id)
            return result
        except Exception:
            self._clear_guild_processing(guild_id)
            raise

    async def _process_queue_items(self, guild_id: Optional[int]) -> None:
        try:
            while True:
                next_item = await self._audio_queue.peek_next(guild_id)
                if not next_item:
                    logger.debug("[QUEUE_ORCHESTRATOR] Queue empty for guild %s", guild_id)
                    break

                item = await self._audio_queue.dequeue(guild_id)
                if item:
                    logger.info("[QUEUE_ORCHESTRATOR] Processing queued item %s", item.item_id)
                    await self._process_item(item)
                    await asyncio.sleep(0.5)
        except Exception as exc:
            logger.error("[QUEUE_ORCHESTRATOR] Error draining queue for guild %s: %s", guild_id, exc, exc_info=True)
        finally:
            self._clear_guild_processing(guild_id)

    def _ensure_guild_processor(self, guild_id: Optional[int]) -> None:
        existing_task = self._guild_processors.get(guild_id)
        if existing_task and not existing_task.done():
            return

        task = asyncio.create_task(self._process_queue_items(guild_id))
        self._guild_processors[guild_id] = task

    def _clear_guild_processing(self, guild_id: Optional[int]) -> None:
        self._processing_guilds.discard(guild_id)
        self._guild_processors.pop(guild_id, None)

    async def _process_item(self, item: AudioQueueItem) -> SpeakTextResult:
        item.mark_processing()
        request = item.request
        audio = None

        try:
            if not request.guild_id:
                error = "Guild ID nao foi fornecido - isolamento de servidor falhou"
                item.mark_failed(error)
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
                return SpeakTextResult(
                    success=False,
                    code=SPEAK_RESULT_CROSS_GUILD_CHANNEL,
                    queued=True,
                    item_id=item.item_id,
                    error_detail=error,
                )

            config = await self._config_repository.load_config_async(request.guild_id)
            config = self._apply_request_override(config, request.config_override)
            audio = await self._tts_engine.generate_audio(request.text, config)

            if not voice_channel.is_connected():
                await voice_channel.connect()

            if request.member_id and not await self._voice_channel_resolution.is_member_in_channel(
                request.member_id, voice_channel
            ):
                error = "Voce saiu do canal de voz"
                item.mark_failed(error)
                return SpeakTextResult(
                    success=False,
                    code=SPEAK_RESULT_USER_LEFT_CHANNEL,
                    queued=True,
                    item_id=item.item_id,
                    error_detail=error,
                )

            try:
                await asyncio.wait_for(voice_channel.play_audio(audio), timeout=60)
                item.mark_completed()
                return SpeakTextResult(
                    success=True,
                    code=SPEAK_RESULT_OK,
                    queued=False,
                    item_id=item.item_id,
                )
            except asyncio.TimeoutError:
                error = "Tempo limite excedido durante reproducao"
                item.mark_failed(error)
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

            error_lower = error_msg.lower()
            if "4017" in error_lower or "dave" in error_lower:
                code = SPEAK_RESULT_VOICE_CONNECTION_FAILED
            elif "not connected" in error_lower or "connection" in error_lower:
                code = SPEAK_RESULT_VOICE_CONNECTION_FAILED
            elif "permission" in error_lower:
                code = SPEAK_RESULT_VOICE_PERMISSION_DENIED
            else:
                code = SPEAK_RESULT_UNKNOWN_ERROR

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
