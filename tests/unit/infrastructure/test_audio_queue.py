"""Tests for audio queue backends."""

from __future__ import annotations

import time

import pytest

from src.core.entities import AudioQueueItem, AudioQueueItemStatus, TTSRequest
from src.infrastructure.audio_queue import RedisAudioQueue


class FakeRedis:
    def __init__(self):
        self._strings: dict[str, str] = {}
        self._lists: dict[str, list[str]] = {}
        self._sets: dict[str, set[str]] = {}
        self._expirations: dict[str, float] = {}

    def _is_expired(self, key: str) -> bool:
        expiration = self._expirations.get(key)
        if expiration is None:
            return False
        if time.time() >= expiration:
            self._strings.pop(key, None)
            self._lists.pop(key, None)
            self._sets.pop(key, None)
            self._expirations.pop(key, None)
            return True
        return False

    async def llen(self, key: str) -> int:
        self._is_expired(key)
        return len(self._lists.get(key, []))

    async def set(self, key: str, value: str, ex: int | None = None, nx: bool = False):
        self._is_expired(key)
        if nx and key in self._strings:
            return False
        self._strings[key] = value
        if ex is not None:
            self._expirations[key] = time.time() + ex
        else:
            self._expirations.pop(key, None)
        return True

    async def rpush(self, key: str, *values: str) -> int:
        self._is_expired(key)
        target = self._lists.setdefault(key, [])
        target.extend(values)
        return len(target)

    async def sadd(self, key: str, *values: str) -> int:
        target = self._sets.setdefault(key, set())
        before = len(target)
        target.update(values)
        return len(target) - before

    async def srem(self, key: str, *values: str) -> int:
        target = self._sets.setdefault(key, set())
        removed = 0
        for value in values:
            if value in target:
                target.remove(value)
                removed += 1
        return removed

    async def smembers(self, key: str) -> set[str]:
        self._is_expired(key)
        return set(self._sets.get(key, set()))

    async def lpop(self, key: str):
        self._is_expired(key)
        values = self._lists.get(key, [])
        if not values:
            return None
        return values.pop(0)

    async def lindex(self, key: str, index: int):
        self._is_expired(key)
        values = self._lists.get(key, [])
        if 0 <= index < len(values):
            return values[index]
        return None

    async def lrange(self, key: str, start: int, end: int):
        self._is_expired(key)
        values = list(self._lists.get(key, []))
        if end == -1:
            end = len(values) - 1
        return values[start : end + 1]

    async def get(self, key: str):
        self._is_expired(key)
        return self._strings.get(key)

    async def delete(self, key: str) -> int:
        removed = 0
        for storage in (self._strings, self._lists, self._sets):
            if key in storage:
                del storage[key]
                removed += 1
        self._expirations.pop(key, None)
        return removed

    async def expire(self, key: str, seconds: int) -> bool:
        if key not in self._strings and key not in self._lists and key not in self._sets:
            return False
        self._expirations[key] = time.time() + seconds
        return True

    async def aclose(self) -> None:
        return None


@pytest.mark.asyncio
class TestRedisAudioQueue:
    async def test_enqueue_and_dequeue_preserve_fifo_per_guild(self):
        queue = RedisAudioQueue(FakeRedis(), max_queue_size=5, key_prefix="test")
        first = AudioQueueItem(request=TTSRequest(text="first", guild_id=1, member_id=10), item_id="item-first")
        second = AudioQueueItem(request=TTSRequest(text="second", guild_id=1, member_id=10), item_id="item-second")

        await queue.enqueue(first)
        await queue.enqueue(second)

        first_out = await queue.dequeue(1)
        second_out = await queue.dequeue(1)

        assert first_out is not None
        assert second_out is not None
        assert first_out.request.text == "first"
        assert second_out.request.text == "second"

    async def test_queues_are_isolated_by_guild(self):
        queue = RedisAudioQueue(FakeRedis(), max_queue_size=5, key_prefix="test")
        guild_one = AudioQueueItem(request=TTSRequest(text="guild-1", guild_id=1, member_id=10), item_id="guild-one")
        guild_two = AudioQueueItem(request=TTSRequest(text="guild-2", guild_id=2, member_id=20), item_id="guild-two")

        await queue.enqueue(guild_one)
        await queue.enqueue(guild_two)

        item = await queue.dequeue(2)

        assert item is not None
        assert item.request.text == "guild-2"
        assert await queue.get_item_position(guild_one.item_id) == 0

    async def test_enqueue_rejects_when_queue_is_full(self):
        queue = RedisAudioQueue(FakeRedis(), max_queue_size=0, key_prefix="test")
        item = AudioQueueItem(request=TTSRequest(text="full", guild_id=1, member_id=10), item_id="full-item")

        item_id = await queue.enqueue(item)
        status = await queue.get_queue_status(1)

        assert item_id is None
        assert status.size == 0
        assert status.items[0].status == AudioQueueItemStatus.FAILED.value

    async def test_get_queue_status_and_clear_completed(self):
        queue = RedisAudioQueue(FakeRedis(), max_queue_size=5, key_prefix="test")
        pending = AudioQueueItem(request=TTSRequest(text="pending", guild_id=1, member_id=10), item_id="pending-item")
        completed = AudioQueueItem(request=TTSRequest(text="done", guild_id=1, member_id=11), item_id="done-item")
        completed.mark_completed()
        completed.completed_at = time.time() - 4000

        await queue.enqueue(pending)
        await queue._store_item(completed)
        await queue._redis.rpush(queue._items_key(1), completed.item_id)

        before = await queue.get_queue_status(1)
        await queue.clear_completed(1, older_than_seconds=3600)
        after = await queue.get_queue_status(1)

        assert before.size == 1
        assert len(before.items) == 2
        assert after.size == 1
        assert [item.id for item in after.items] == [pending.item_id]

    async def test_update_item_persists_processed_status(self):
        queue = RedisAudioQueue(FakeRedis(), max_queue_size=5, key_prefix="test")
        item = AudioQueueItem(request=TTSRequest(text="speak", guild_id=1, member_id=10), item_id="item-status")

        await queue.enqueue(item)
        dequeued = await queue.dequeue(1)

        assert dequeued is not None
        dequeued.mark_processing()
        await queue.update_item(dequeued)
        status = await queue.get_queue_status(1)
        assert status.items[0].status == AudioQueueItemStatus.PROCESSING.value

        dequeued.mark_completed()
        await queue.update_item(dequeued)
        status = await queue.get_queue_status(1)
        assert status.items[0].status == AudioQueueItemStatus.COMPLETED.value

    async def test_completed_items_expire_after_observability_ttl(self):
        fake_redis = FakeRedis()
        queue = RedisAudioQueue(fake_redis, max_queue_size=5, key_prefix="test", completed_item_ttl_seconds=1)
        item = AudioQueueItem(request=TTSRequest(text="speak", guild_id=1, member_id=10), item_id="item-expire")

        await queue.enqueue(item)
        dequeued = await queue.dequeue(1)

        assert dequeued is not None
        dequeued.mark_completed()
        await queue.update_item(dequeued)

        status = await queue.get_queue_status(1)
        assert len(status.items) == 1

        fake_redis._expirations[queue._item_key(dequeued.item_id)] = time.time() - 1
        status = await queue.get_queue_status(1)
        assert status.items == []

    async def test_acquire_and_release_guild_lock(self):
        queue = RedisAudioQueue(FakeRedis(), max_queue_size=5, key_prefix="test")

        assert await queue.acquire_guild_lock(1, "worker-a") is True
        assert await queue.acquire_guild_lock(1, "worker-b") is False

        await queue.release_guild_lock(1, "worker-a")

        assert await queue.acquire_guild_lock(1, "worker-b") is True

    async def test_renew_guild_lock_extends_existing_lock(self):
        fake_redis = FakeRedis()
        queue = RedisAudioQueue(fake_redis, max_queue_size=5, key_prefix="test")

        assert await queue.acquire_guild_lock(1, "worker-a", ttl_seconds=5) is True
        original_expiration = fake_redis._expirations[queue._lock_key(1)]

        renewed = await queue.renew_guild_lock(1, "worker-a", ttl_seconds=20)

        assert renewed is True
        assert fake_redis._expirations[queue._lock_key(1)] > original_expiration

    async def test_processing_lease_reflects_active_guild_playback(self):
        fake_redis = FakeRedis()
        queue = RedisAudioQueue(fake_redis, max_queue_size=5, key_prefix="test")

        assert await queue.is_guild_processing(1) is False
        assert await queue.acquire_processing_lease(1, "worker-a", ttl_seconds=5) is True
        assert await queue.is_guild_processing(1) is True
        assert await queue.acquire_processing_lease(1, "worker-b", ttl_seconds=5) is False

        original_expiration = fake_redis._expirations[queue._processing_key(1)]
        renewed = await queue.renew_processing_lease(1, "worker-a", ttl_seconds=20)

        assert renewed is True
        assert fake_redis._expirations[queue._processing_key(1)] > original_expiration

        await queue.release_processing_lease(1, "worker-a")

        assert await queue.is_guild_processing(1) is False
