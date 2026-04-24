"""Integration tests for RedisAudioQueue against a real Redis service."""

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
import pytest_asyncio

from src.core.entities import AudioQueueItem, AudioQueueItemStatus, TTSRequest
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
        max_queue_size=5,
        key_prefix=f"test-{uuid.uuid4().hex}",
        completed_item_ttl_seconds=1,
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


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.redis
async def test_redis_queue_preserves_fifo_and_refreshes_positions(redis_queue: RedisAudioQueue):
    first = _build_item(text="first", guild_id=1, member_id=10, item_id="item-first")
    second = _build_item(text="second", guild_id=1, member_id=10, item_id="item-second")

    assert await redis_queue.enqueue(first) == "item-first"
    assert await redis_queue.enqueue(second) == "item-second"
    assert await redis_queue.get_item_position("item-first") == 0
    assert await redis_queue.get_item_position("item-second") == 1

    dequeued = await redis_queue.dequeue(1)

    assert dequeued is not None
    assert dequeued.item_id == "item-first"
    assert await redis_queue.get_item_position("item-second") == 0

    status = await redis_queue.get_queue_status(1)

    assert status.size == 1
    assert [item.id for item in status.items] == ["item-first", "item-second"]


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.redis
async def test_redis_queue_expires_completed_items_and_rewrites_history(redis_queue: RedisAudioQueue):
    item = _build_item(text="complete-me", guild_id=7, member_id=77, item_id="item-complete")

    await redis_queue.enqueue(item)
    dequeued = await redis_queue.dequeue(7)

    assert dequeued is not None
    dequeued.mark_completed()
    await redis_queue.update_item(dequeued)

    initial_status = await redis_queue.get_queue_status(7)
    assert len(initial_status.items) == 1
    assert initial_status.items[0].status == AudioQueueItemStatus.COMPLETED.value

    await asyncio.sleep(1.2)

    expired_status = await redis_queue.get_queue_status(7)
    assert expired_status.items == []


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.redis
async def test_redis_queue_uses_real_lock_and_processing_lease_semantics(redis_queue: RedisAudioQueue):
    assert await redis_queue.acquire_guild_lock(42, "worker-a", ttl_seconds=5) is True
    assert await redis_queue.acquire_guild_lock(42, "worker-b", ttl_seconds=5) is False
    assert await redis_queue.renew_guild_lock(42, "worker-a", ttl_seconds=5) is True
    assert await redis_queue.renew_guild_lock(42, "worker-b", ttl_seconds=5) is False

    await redis_queue.release_guild_lock(42, "worker-a")

    assert await redis_queue.acquire_guild_lock(42, "worker-b", ttl_seconds=5) is True
    assert await redis_queue.acquire_processing_lease(42, "worker-b", ttl_seconds=5) is True
    assert await redis_queue.is_guild_processing(42) is True
    assert await redis_queue.acquire_processing_lease(42, "worker-c", ttl_seconds=5) is False
    assert await redis_queue.renew_processing_lease(42, "worker-b", ttl_seconds=5) is True

    await redis_queue.release_processing_lease(42, "worker-b")

    assert await redis_queue.is_guild_processing(42) is False
