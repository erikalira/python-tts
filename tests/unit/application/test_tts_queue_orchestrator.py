"""Focused tests for queue draining and playback orchestration."""

import asyncio

import pytest

from src.application.results import SPEAK_RESULT_OK, SPEAK_RESULT_UNKNOWN_ERROR
from src.application.tts_queue_orchestrator import TTSQueueOrchestrator
from src.application.voice_channel_resolution import VoiceChannelResolutionService
from src.core.entities import AudioQueueItem, TTSRequest
from src.infrastructure.audio_queue import InMemoryAudioQueue
from tests.conftest import MockAudioCleanup, MockConfigRepository, MockTTSEngine, MockVoiceChannelRepository


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

    async def test_background_processor_drains_followup_items(self):
        queue = InMemoryAudioQueue()
        orchestrator = TTSQueueOrchestrator(
            tts_engine=MockTTSEngine(),
            config_repository=MockConfigRepository(),
            audio_queue=queue,
            voice_channel_resolution=VoiceChannelResolutionService(MockVoiceChannelRepository()),
            audio_cleanup=MockAudioCleanup(),
        )

        processed = []
        release = asyncio.Event()

        async def fake_process_item(item):
            processed.append(item.request.text)
            if item.request.text == "second":
                release.set()
            return type("FakeResult", (), {"code": SPEAK_RESULT_OK, "success": True})()

        orchestrator._process_item = fake_process_item

        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="first", guild_id=789012, member_id=1)))
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="second", guild_id=789012, member_id=1)))

        first_result = await orchestrator.start_processing_for_item(789012)
        assert first_result.code == SPEAK_RESULT_OK

        await asyncio.wait_for(release.wait(), timeout=1)
        await asyncio.sleep(0.6)

        assert processed == ["first", "second"]
        assert orchestrator.is_processing(789012) is False
