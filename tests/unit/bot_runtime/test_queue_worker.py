"""Tests for Discord bot queue worker."""

import asyncio

import pytest

from src.application.dto import SPEAK_RESULT_OK, SpeakTextResult
from src.bot_runtime.queue_worker import BotQueueWorker
from src.core.entities import AudioQueueItem, TTSRequest
from src.infrastructure.audio_queue import InMemoryAudioQueue


@pytest.mark.asyncio
class TestBotQueueWorker:
    async def test_worker_drains_single_guild_in_fifo_order(self):
        queue = InMemoryAudioQueue()
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="first", guild_id=1, member_id=10)))
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="second", guild_id=1, member_id=10)))
        processed: list[str] = []
        finished = asyncio.Event()

        class FakeOrchestrator:
            async def start_processing_for_item(self, guild_id):
                item = await queue.dequeue(guild_id)
                if item is not None:
                    processed.append(item.request.text)
                if len(processed) == 2:
                    finished.set()
                return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)

        worker = BotQueueWorker(audio_queue=queue, queue_orchestrator=FakeOrchestrator(), poll_interval_seconds=0.01)
        await worker.start()

        await asyncio.wait_for(finished.wait(), timeout=1)
        await worker.stop()

        assert processed == ["first", "second"]

    async def test_worker_processes_different_guilds_in_parallel(self):
        queue = InMemoryAudioQueue()
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="guild-1", guild_id=1, member_id=10)))
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="guild-2", guild_id=2, member_id=20)))
        guild_one_started = asyncio.Event()
        guild_two_processed = asyncio.Event()
        release_guild_one = asyncio.Event()

        class FakeOrchestrator:
            async def start_processing_for_item(self, guild_id):
                item = await queue.dequeue(guild_id)
                if item is None:
                    return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)
                if guild_id == 1:
                    guild_one_started.set()
                    await release_guild_one.wait()
                else:
                    guild_two_processed.set()
                return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)

        worker = BotQueueWorker(audio_queue=queue, queue_orchestrator=FakeOrchestrator(), poll_interval_seconds=0.01)
        await worker.start()

        await asyncio.wait_for(guild_one_started.wait(), timeout=1)
        await asyncio.wait_for(guild_two_processed.wait(), timeout=1)
        release_guild_one.set()
        await worker.stop()

        assert guild_two_processed.is_set()

    async def test_worker_uses_guild_lock_to_prevent_duplicate_processing(self):
        queue = InMemoryAudioQueue()
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="first", guild_id=1, member_id=10)))
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="second", guild_id=1, member_id=10)))
        active_processors = 0
        max_active_processors = 0
        processed: list[str] = []
        release = asyncio.Event()

        class FakeOrchestrator:
            async def start_processing_for_item(self, guild_id):
                nonlocal active_processors, max_active_processors
                item = await queue.dequeue(guild_id)
                if item is None:
                    return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)

                active_processors += 1
                max_active_processors = max(max_active_processors, active_processors)
                processed.append(item.request.text)
                if len(processed) == 1:
                    await release.wait()
                active_processors -= 1
                return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)

        worker_one = BotQueueWorker(audio_queue=queue, queue_orchestrator=FakeOrchestrator(), poll_interval_seconds=0.01)
        worker_two = BotQueueWorker(audio_queue=queue, queue_orchestrator=FakeOrchestrator(), poll_interval_seconds=0.01)

        await worker_one.start()
        await worker_two.start()
        await asyncio.sleep(0.1)
        release.set()
        await asyncio.sleep(0.1)
        await worker_one.stop()
        await worker_two.stop()

        assert processed == ["first", "second"]
        assert max_active_processors == 1

    async def test_worker_renews_guild_lock_during_long_processing(self):
        class RenewalQueue(InMemoryAudioQueue):
            def __init__(self):
                super().__init__()
                self.renew_calls = 0

            async def renew_guild_lock(self, guild_id, owner_token: str, ttl_seconds: int = 30) -> bool:
                del guild_id, owner_token, ttl_seconds
                self.renew_calls += 1
                return True

        queue = RenewalQueue()
        await queue.enqueue(AudioQueueItem(request=TTSRequest(text="long", guild_id=1, member_id=10)))
        release = asyncio.Event()

        class FakeOrchestrator:
            async def start_processing_for_item(self, guild_id):
                item = await queue.dequeue(guild_id)
                if item is None:
                    return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)
                await release.wait()
                return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)

        worker = BotQueueWorker(
            audio_queue=queue,
            queue_orchestrator=FakeOrchestrator(),
            poll_interval_seconds=0.01,
            guild_lock_ttl_seconds=3,
            guild_lock_renew_interval_seconds=0.01,
        )
        await worker.start()
        await asyncio.sleep(0.05)
        release.set()
        await asyncio.sleep(0.05)
        await worker.stop()

        assert queue.renew_calls > 0
