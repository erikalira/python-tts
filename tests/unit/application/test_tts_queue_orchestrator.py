"""Focused tests for queue draining and playback orchestration."""

import asyncio
from contextlib import contextmanager

import pytest

from src.application.dto import (
    SPEAK_RESULT_CROSS_GUILD_CHANNEL,
    SPEAK_RESULT_GENERATION_TIMEOUT,
    SPEAK_RESULT_MISSING_GUILD_ID,
    SPEAK_RESULT_OK,
    SPEAK_RESULT_UNKNOWN_ERROR,
    SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
)
from src.application.tts_queue_orchestrator import TTSQueueOrchestrator
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.core.entities import AudioQueueItem, TTSConfig, TTSRequest
from src.infrastructure.audio_queue import InMemoryAudioQueue
from tests.conftest import (
    MockAudioCleanup,
    MockConfigRepository,
    MockTTSEngine,
    MockVoiceChannel,
    MockVoiceChannelRepository,
)


class RecordingTelemetry:
    def __init__(self):
        self.processing_results = []

    def record_submission_result(self, *, request, accepted: bool, code: str, engine: str) -> None:
        del request, accepted, code, engine

    def record_processing_result(self, *, item: AudioQueueItem, success: bool, code: str, engine: str) -> None:
        self.processing_results.append(
            {
                "item_id": item.item_id,
                "success": success,
                "code": code,
                "engine": engine,
            }
        )

    def snapshot(self):
        return None


class RecordingOtelRuntime:
    def __init__(self):
        self.processed_items = []

    @contextmanager
    def start_internal_span(self, name: str, *, attributes=None):
        del name, attributes
        yield RecordingSpan()

    def record_queue_item_processed(
        self,
        *,
        guild_id: int | None,
        engine: str,
        result_code: str,
        success: bool,
        timeout_flag: bool,
    ) -> None:
        self.processed_items.append(
            {
                "guild_id": guild_id,
                "engine": engine,
                "result_code": result_code,
                "success": success,
                "timeout_flag": timeout_flag,
            }
        )


class RecordingSpan:
    def set_attribute(self, key: str, value) -> None:
        del key, value


@pytest.mark.asyncio
class TestTTSQueueOrchestrator:
    async def test_start_processing_returns_unknown_error_when_item_disappears(self):
        queue = InMemoryAudioQueue()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=MockTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=MockAudioCleanup(),
        )

        result = await orchestrator.start_processing_for_item(789012)

        assert result.code == SPEAK_RESULT_UNKNOWN_ERROR
        assert result.success is False
        assert orchestrator.is_processing(789012) is False

    async def test_start_processing_handles_single_item_and_cleans_up_audio(self):
        queue = InMemoryAudioQueue()
        cleanup = MockAudioCleanup()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=MockTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=cleanup,
        )
        item = AudioQueueItem(
            request=TTSRequest(text="hello", guild_id=789012, member_id=345678, channel_id=123456)
        )
        await queue.enqueue(item)

        result = await orchestrator.start_processing_for_item(789012)

        assert result.code == SPEAK_RESULT_OK
        assert cleanup.cleaned_paths == ["/tmp/mock_audio.wav"]

    async def test_start_processing_handles_only_one_item_per_call(self):
        queue = InMemoryAudioQueue()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=MockTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=MockAudioCleanup(),
        )

        processed = []

        async def fake_process_item(item):
            processed.append(item.request.text)
            return type("FakeResult", (), {"code": SPEAK_RESULT_OK, "success": True})()

        orchestrator._process_item = fake_process_item

        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="first", guild_id=789012, member_id=1)))
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="second", guild_id=789012, member_id=1)))

        first_result = await orchestrator.start_processing_for_item(789012)
        assert first_result.code == SPEAK_RESULT_OK
        assert processed == ["first"]
        next_item = await queue.peek_next(789012)
        assert next_item is not None
        assert next_item.request.text == "second"
        assert orchestrator.is_processing(789012) is False

    async def test_process_item_uses_guild_specific_engine_from_config(self):
        queue = InMemoryAudioQueue()
        config_repository = MockConfigRepository()
        await config_repository.save_config_async(
            789012,
            TTSConfig(
                engine="pyttsx3",
                language="en",
                voice_id="en-us",
                rate=180,
            ),
        )
        tts_engine = MockTTSEngine()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=tts_engine,
            config_repository=config_repository,
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=MockAudioCleanup(),
        )
        item = AudioQueueItem(
            request=TTSRequest(text="robot", guild_id=789012, member_id=345678, channel_id=123456)
        )

        result = await orchestrator._process_item(item)

        assert result.code == SPEAK_RESULT_OK
        assert tts_engine.calls[0]["config"].engine == "pyttsx3"

    async def test_process_item_rejects_requests_without_guild_id(self):
        queue = InMemoryAudioQueue()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=MockTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=MockAudioCleanup(),
        )
        item = AudioQueueItem(
            request=TTSRequest(text="sem guild", guild_id=None, member_id=345678, channel_id=123456)
        )

        result = await orchestrator._process_item(item)

        assert result.code == SPEAK_RESULT_MISSING_GUILD_ID
        assert result.success is False
        assert item.status == "failed"

    async def test_process_item_returns_not_found_when_voice_resolution_fails(self):
        queue = InMemoryAudioQueue()
        telemetry = RecordingTelemetry()
        otel_runtime = RecordingOtelRuntime()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=MockTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository(return_none=True)),
            audio_cleanup=MockAudioCleanup(),
            telemetry=telemetry,
            otel_runtime=otel_runtime,
        )
        item = AudioQueueItem(
            request=TTSRequest(text="sem canal", guild_id=789012, member_id=345678, channel_id=123456)
        )

        result = await orchestrator._process_item(item)

        assert result.code == SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND
        assert result.success is False
        assert item.status == "failed"
        assert telemetry.processing_results == [
            {
                "item_id": item.item_id,
                "success": False,
                "code": SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
                "engine": "configured_default",
            }
        ]
        assert otel_runtime.processed_items == [
            {
                "guild_id": 789012,
                "engine": "configured_default",
                "result_code": SPEAK_RESULT_VOICE_CHANNEL_NOT_FOUND,
                "success": False,
                "timeout_flag": False,
            }
        ]

    async def test_process_item_rejects_cross_guild_voice_channel(self):
        queue = InMemoryAudioQueue()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=MockTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(
                MockVoiceChannelRepository(MockVoiceChannel(guild_id=999999))
            ),
            audio_cleanup=MockAudioCleanup(),
        )
        item = AudioQueueItem(
            request=TTSRequest(text="guild errado", guild_id=789012, member_id=345678, channel_id=123456)
        )

        result = await orchestrator._process_item(item)

        assert result.code == SPEAK_RESULT_CROSS_GUILD_CHANNEL
        assert result.success is False

    async def test_process_item_applies_per_request_voice_override_without_persisting_it(self):
        queue = InMemoryAudioQueue()
        config_repository = MockConfigRepository()
        tts_engine = MockTTSEngine()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=tts_engine,
            config_repository=config_repository,
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=MockAudioCleanup(),
        )
        item = AudioQueueItem(
            request=TTSRequest(
                text="override",
                guild_id=789012,
                member_id=345678,
                channel_id=123456,
                config_override=TTSConfig(
                    engine="edge-tts",
                    language="pt-BR",
                    voice_id="pt-BR-FranciscaNeural",
                    rate=180,
                ),
            )
        )

        result = await orchestrator._process_item(item)

        assert result.code == SPEAK_RESULT_OK
        assert tts_engine.calls[0]["config"].engine == "edge-tts"
        assert config_repository.get_config(789012).engine == "gtts"

    async def test_process_item_fails_fast_when_audio_generation_hangs(self):
        class HangingTTSEngine(MockTTSEngine):
            async def generate_audio(self, text: str, config: TTSConfig):
                self.calls.append({"text": text, "config": config})
                await asyncio.Future()

        queue = InMemoryAudioQueue()
        cleanup = MockAudioCleanup()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=HangingTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=cleanup,
            generation_timeout_seconds=0.01,
        )
        item = AudioQueueItem(
            request=TTSRequest(text="edge hang", guild_id=789012, member_id=345678, channel_id=123456)
        )

        result = await orchestrator._process_item(item)

        assert result.code == SPEAK_RESULT_GENERATION_TIMEOUT
        assert result.success is False
        assert cleanup.cleaned_paths == []

    async def test_process_item_records_generation_timeout_in_runtime_telemetry(self):
        class HangingTTSEngine(MockTTSEngine):
            async def generate_audio(self, text: str, config: TTSConfig):
                self.calls.append({"text": text, "config": config})
                await asyncio.Future()

        queue = InMemoryAudioQueue()
        telemetry = RecordingTelemetry()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=HangingTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=MockAudioCleanup(),
            generation_timeout_seconds=0.01,
            telemetry=telemetry,
        )
        item = AudioQueueItem(
            request=TTSRequest(text="edge hang", guild_id=789012, member_id=345678, channel_id=123456)
        )

        result = await orchestrator._process_item(item)

        assert result.code == SPEAK_RESULT_GENERATION_TIMEOUT
        assert telemetry.processing_results == [
            {
                "item_id": item.item_id,
                "success": False,
                "code": SPEAK_RESULT_GENERATION_TIMEOUT,
                "engine": "configured_default",
            }
        ]
