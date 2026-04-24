"""Redis-backed integration tests for distributed BotQueueWorker behavior."""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
import pytest_asyncio

from src.application.dto import SPEAK_RESULT_OK, SpeakTextResult
from src.bot_runtime.queue_worker import BotQueueWorker
from src.core.entities import AudioQueueItem, TTSRequest
from src.infrastructure.audio_queue import RedisAudioQueue

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover - exercised only when the optional dependency is absent.
    Redis = None


def _require_redis_integration() -> None:
    if os.getenv("RUN_REDIS_INTEGRATION_TESTS") != "1":
        pytest.skip("Set RUN_REDIS_INTEGRATION_TESTS=1 to run Redis integration tests")
    if Redis is None:
        pytest.skip("redis package is not installed")


@pytest_asyncio.fixture
async def redis_queue():
    _require_redis_integration()
    redis_client = Redis(
        host=os.getenv("REDIS_HOST", "127.0.0.1"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "15")),
        password=os.getenv("REDIS_PASSWORD") or None,
        decode_responses=False,
    )
    await redis_client.flushdb()

    queue = RedisAudioQueue(
        redis_client,
        max_queue_size=10,
        key_prefix=f"worker-test-{uuid.uuid4().hex}",
        completed_item_ttl_seconds=5,
    )

    try:
        yield queue
    finally:
        await redis_client.flushdb()
        await queue.aclose()


def _build_item(*, text: str, guild_id: int, member_id: int, item_id: str) -> AudioQueueItem:
    return AudioQueueItem(
        request=TTSRequest(text=text, guild_id=guild_id, member_id=member_id),
        item_id=item_id,
    )


async def _seed_orphan_processing_lease(queue: RedisAudioQueue, guild_id: int, *, owner_token: str, ttl_seconds: int) -> None:
    await queue._redis.set(queue._processing_key(guild_id), owner_token, ex=ttl_seconds)


async def _seed_orphan_guild_lock(queue: RedisAudioQueue, guild_id: int, *, owner_token: str, ttl_seconds: int) -> None:
    await queue._redis.set(queue._lock_key(guild_id), owner_token, ex=ttl_seconds)


class _CoordinatedOrchestrator:
    def __init__(self, queue: RedisAudioQueue):
        self._queue = queue
        self.processed: list[str] = []
        self.active_processors = 0
        self.max_active_processors = 0
        self.first_started = asyncio.Event()
        self.release_first = asyncio.Event()
        self.all_processed = asyncio.Event()

    async def start_processing_for_item(self, guild_id):
        item = await self._queue.dequeue(guild_id)
        if item is None:
            return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)

        self.active_processors += 1
        self.max_active_processors = max(self.max_active_processors, self.active_processors)
        self.processed.append(item.request.text)
        if len(self.processed) == 1:
            self.first_started.set()
            await self.release_first.wait()
        if len(self.processed) >= 2:
            self.all_processed.set()
        self.active_processors -= 1
        return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)


class _RecordingOrchestrator:
    def __init__(self, queue: RedisAudioQueue):
        self._queue = queue
        self.processed: list[str] = []
        self.processed_event = asyncio.Event()

    async def start_processing_for_item(self, guild_id):
        item = await self._queue.dequeue(guild_id)
        if item is None:
            return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)
        self.processed.append(item.request.text)
        self.processed_event.set()
        return SpeakTextResult(success=True, code=SPEAK_RESULT_OK, queued=False)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.redis
async def test_workers_compete_for_same_guild_without_parallel_processing(redis_queue: RedisAudioQueue):
    await redis_queue.enqueue(_build_item(text="first", guild_id=1, member_id=10, item_id="item-first"))
    await redis_queue.enqueue(_build_item(text="second", guild_id=1, member_id=10, item_id="item-second"))
    orchestrator = _CoordinatedOrchestrator(redis_queue)
    worker_one = BotQueueWorker(
        audio_queue=redis_queue,
        queue_orchestrator=orchestrator,
        poll_interval_seconds=0.01,
        guild_lock_ttl_seconds=2,
        guild_lock_renew_interval_seconds=0.2,
        processing_lease_ttl_seconds=2,
        processing_lease_renew_interval_seconds=0.2,
    )
    worker_two = BotQueueWorker(
        audio_queue=redis_queue,
        queue_orchestrator=orchestrator,
        poll_interval_seconds=0.01,
        guild_lock_ttl_seconds=2,
        guild_lock_renew_interval_seconds=0.2,
        processing_lease_ttl_seconds=2,
        processing_lease_renew_interval_seconds=0.2,
    )

    await worker_one.start()
    await worker_two.start()

    try:
        await asyncio.wait_for(orchestrator.first_started.wait(), timeout=2)
        await asyncio.sleep(0.3)
        assert orchestrator.max_active_processors == 1
        assert orchestrator.processed == ["first"]

        orchestrator.release_first.set()
        await asyncio.wait_for(orchestrator.all_processed.wait(), timeout=2)
        assert orchestrator.processed == ["first", "second"]
        assert orchestrator.max_active_processors == 1
    finally:
        await worker_one.stop()
        await worker_two.stop()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.redis
async def test_worker_recovers_after_orphan_processing_lease_expires(redis_queue: RedisAudioQueue):
    guild_id = 7
    await redis_queue.enqueue(_build_item(text="lease-recovery", guild_id=guild_id, member_id=70, item_id="item-lease"))
    await _seed_orphan_processing_lease(redis_queue, guild_id, owner_token="crashed-worker", ttl_seconds=1)
    orchestrator = _RecordingOrchestrator(redis_queue)
    worker = BotQueueWorker(
        audio_queue=redis_queue,
        queue_orchestrator=orchestrator,
        poll_interval_seconds=0.01,
        guild_lock_ttl_seconds=3,
        guild_lock_renew_interval_seconds=0.2,
        processing_lease_ttl_seconds=3,
        processing_lease_renew_interval_seconds=0.2,
    )

    await worker.start()

    try:
        await asyncio.wait_for(orchestrator.processed_event.wait(), timeout=3)
        assert orchestrator.processed == ["lease-recovery"]
    finally:
        await worker.stop()


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.redis
async def test_worker_recovers_after_orphan_guild_lock_expires(redis_queue: RedisAudioQueue):
    guild_id = 9
    await redis_queue.enqueue(_build_item(text="lock-recovery", guild_id=guild_id, member_id=90, item_id="item-lock"))
    await _seed_orphan_guild_lock(redis_queue, guild_id, owner_token="crashed-worker", ttl_seconds=1)
    orchestrator = _RecordingOrchestrator(redis_queue)
    worker = BotQueueWorker(
        audio_queue=redis_queue,
        queue_orchestrator=orchestrator,
        poll_interval_seconds=0.01,
        guild_lock_ttl_seconds=3,
        guild_lock_renew_interval_seconds=0.2,
        processing_lease_ttl_seconds=3,
        processing_lease_renew_interval_seconds=0.2,
    )

    await worker.start()

    try:
        await asyncio.wait_for(orchestrator.processed_event.wait(), timeout=3)
        assert orchestrator.processed == ["lock-recovery"]
    finally:
        await worker.stop()
