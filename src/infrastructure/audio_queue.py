"""Audio queue implementations for Discord bot delivery."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Any, Optional

from src.application.dto import AudioQueueItemStatusDTO, AudioQueueStatusDTO
from src.core.entities import AudioQueueItem, AudioQueueItemStatus, TTSConfig, TTSRequest
from src.core.interfaces import IAudioQueue
from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime

try:  # pragma: no cover - exercised through runtime wiring when dependency is installed.
    from redis.asyncio import Redis as RedisClient
except ImportError:  # pragma: no cover - local tests can still exercise the queue with a fake client.
    RedisClient = Any

logger = logging.getLogger(__name__)


def _normalize_guild_id(guild_id: Optional[int]) -> str:
    return str(guild_id) if guild_id is not None else "noguild"


def _request_to_payload(request: TTSRequest) -> dict[str, Any]:
    override = request.config_override
    return {
        "text": request.text,
        "channel_id": request.channel_id,
        "guild_id": request.guild_id,
        "member_id": request.member_id,
        "config_override": None
        if override is None
        else {
            "engine": override.engine,
            "language": override.language,
            "voice_id": override.voice_id,
            "rate": override.rate,
            "output_device": override.output_device,
        },
    }


def _request_from_payload(payload: dict[str, Any]) -> TTSRequest:
    override = payload.get("config_override")
    config_override = None
    if isinstance(override, dict):
        config_override = TTSConfig(
            engine=str(override.get("engine", "gtts")),
            language=str(override.get("language", "pt")),
            voice_id=str(override.get("voice_id", "roa/pt-br")),
            rate=int(override.get("rate", 180)),
            output_device=override.get("output_device"),
        )

    return TTSRequest(
        text=str(payload.get("text", "")),
        channel_id=payload.get("channel_id"),
        guild_id=payload.get("guild_id"),
        member_id=payload.get("member_id"),
        config_override=config_override,
    )


def _item_to_payload(item: AudioQueueItem) -> dict[str, Any]:
    return {
        "item_id": item.item_id,
        "status": item.status.value,
        "created_at": item.created_at,
        "started_at": item.started_at,
        "completed_at": item.completed_at,
        "error_message": item.error_message,
        "trace_context": item.trace_context,
        "position_in_queue": item.position_in_queue,
        "request": _request_to_payload(item.request),
    }


def _item_from_payload(payload: dict[str, Any]) -> AudioQueueItem:
    return AudioQueueItem(
        request=_request_from_payload(payload["request"]),
        item_id=str(payload["item_id"]),
        status=AudioQueueItemStatus(str(payload.get("status", AudioQueueItemStatus.PENDING.value))),
        created_at=float(payload.get("created_at", time.time())),
        started_at=payload.get("started_at"),
        completed_at=payload.get("completed_at"),
        error_message=payload.get("error_message"),
        trace_context=payload.get("trace_context"),
        position_in_queue=int(payload.get("position_in_queue", 0)),
    )


def _build_status_dto(item: AudioQueueItem) -> AudioQueueItemStatusDTO:
    return AudioQueueItemStatusDTO(
        id=item.item_id,
        user_id=item.request.member_id,
        status=item.status.value,
        position=item.position_in_queue,
        wait_time_seconds=round(item.wait_time_seconds, 1),
    )


class InMemoryAudioQueue(IAudioQueue):
    """In-memory audio queue per guild for safe multi-user handling."""

    def __init__(
        self,
        max_queue_size: int = 50,
        max_queue_wait_seconds: int = 3600,
        telemetry: OpenTelemetryRuntime | None = None,
    ):
        self._queues: dict[Optional[int], list[AudioQueueItem]] = {}
        self._history: dict[Optional[int], list[AudioQueueItem]] = {}
        self._lock = asyncio.Lock()
        self._guild_locks: dict[Optional[int], str] = {}
        self._processing_leases: dict[Optional[int], str] = {}
        self._max_queue_size = max_queue_size
        self._max_queue_wait = max_queue_wait_seconds
        self._telemetry = telemetry

    async def enqueue(self, item: AudioQueueItem) -> Optional[str]:
        async with self._lock:
            guild_id = item.request.guild_id
            queue = self._queues.setdefault(guild_id, [])
            history = self._history.setdefault(guild_id, [])

            if len(queue) >= self._max_queue_size:
                logger.warning("[QUEUE] Guild %s queue full (%s items)", guild_id, self._max_queue_size)
                item.mark_failed("Fila de audio cheia. Tente novamente mais tarde.")
                history.append(item)
                return None

            item.position_in_queue = len(queue)
            queue.append(item)
            history.append(item)
            self._record_queue_metrics_unlocked(guild_id, queue)
            logger.info(
                "[QUEUE] Item %s enqueued to guild %s, position: %s, from user %s",
                item.item_id,
                guild_id,
                item.position_in_queue,
                item.request.member_id,
            )
            return item.item_id

    async def dequeue(self, guild_id: Optional[int]) -> Optional[AudioQueueItem]:
        async with self._lock:
            queue = self._queues.get(guild_id)
            if not queue:
                return None

            item = queue.pop(0)
            await self._refresh_positions_unlocked(guild_id)
            self._record_queue_metrics_unlocked(guild_id, queue)
            logger.info("[QUEUE] Item %s dequeued from guild %s", item.item_id, guild_id)
            return item

    async def peek_next(self, guild_id: Optional[int]) -> Optional[AudioQueueItem]:
        async with self._lock:
            queue = self._queues.get(guild_id)
            return queue[0] if queue else None

    async def get_queue_status(self, guild_id: Optional[int]) -> AudioQueueStatusDTO:
        async with self._lock:
            items = self._history.get(guild_id, [])
            return AudioQueueStatusDTO(
                size=len(self._queues.get(guild_id, [])),
                items=[_build_status_dto(item) for item in items],
            )

    async def get_item_position(self, item_id: str) -> int:
        async with self._lock:
            for guild_queue in self._queues.values():
                for index, item in enumerate(guild_queue):
                    if item.item_id == item_id:
                        return index
            return -1

    async def update_item(self, item: AudioQueueItem) -> None:
        async with self._lock:
            guild_id = item.request.guild_id
            history = self._history.get(guild_id, [])
            for index, existing_item in enumerate(history):
                if existing_item.item_id == item.item_id:
                    history[index] = item
                    break

    async def clear_completed(self, guild_id: Optional[int], older_than_seconds: int = 3600):
        async with self._lock:
            now = time.time()
            history = self._history.get(guild_id, [])
            self._history[guild_id] = [
                item
                for item in history
                if item.status in (AudioQueueItemStatus.PENDING, AudioQueueItemStatus.PROCESSING)
                or (item.completed_at and now - item.completed_at < older_than_seconds)
            ]

    async def list_guild_ids(self) -> list[Optional[int]]:
        async with self._lock:
            return [guild_id for guild_id, queue in self._queues.items() if queue]

    async def acquire_guild_lock(self, guild_id: Optional[int], owner_token: str, ttl_seconds: int = 30) -> bool:
        del ttl_seconds
        async with self._lock:
            current = self._guild_locks.get(guild_id)
            if current and current != owner_token:
                return False
            self._guild_locks[guild_id] = owner_token
            return True

    async def release_guild_lock(self, guild_id: Optional[int], owner_token: str) -> None:
        async with self._lock:
            if self._guild_locks.get(guild_id) == owner_token:
                self._guild_locks.pop(guild_id, None)

    async def renew_guild_lock(self, guild_id: Optional[int], owner_token: str, ttl_seconds: int = 30) -> bool:
        del ttl_seconds
        async with self._lock:
            return self._guild_locks.get(guild_id) == owner_token

    async def acquire_processing_lease(
        self,
        guild_id: Optional[int],
        owner_token: str,
        ttl_seconds: int = 30,
    ) -> bool:
        del ttl_seconds
        async with self._lock:
            current = self._processing_leases.get(guild_id)
            if current and current != owner_token:
                return False
            self._processing_leases[guild_id] = owner_token
            return True

    async def release_processing_lease(self, guild_id: Optional[int], owner_token: str) -> None:
        async with self._lock:
            if self._processing_leases.get(guild_id) == owner_token:
                self._processing_leases.pop(guild_id, None)

    async def renew_processing_lease(
        self,
        guild_id: Optional[int],
        owner_token: str,
        ttl_seconds: int = 30,
    ) -> bool:
        del ttl_seconds
        async with self._lock:
            return self._processing_leases.get(guild_id) == owner_token

    async def is_guild_processing(self, guild_id: Optional[int]) -> bool:
        async with self._lock:
            return guild_id in self._processing_leases

    async def _refresh_positions_unlocked(self, guild_id: Optional[int]) -> None:
        queue = self._queues.get(guild_id, [])
        for index, remaining_item in enumerate(queue):
            remaining_item.position_in_queue = index

    def _record_queue_metrics_unlocked(self, guild_id: Optional[int], queue: list[AudioQueueItem]) -> None:
        if self._telemetry is None:
            return
        self._telemetry.record_queue_depth(guild_id=guild_id, depth=len(queue))
        if queue:
            oldest_item = min(queue, key=lambda item: item.created_at)
            self._telemetry.record_queue_age(
                guild_id=guild_id,
                age_seconds=time.time() - oldest_item.created_at,
            )

class RedisAudioQueue(IAudioQueue):
    """Redis-backed FIFO queue with item metadata per guild."""

    def __init__(
        self,
        redis_client: Any,
        *,
        max_queue_size: int = 50,
        max_queue_wait_seconds: int = 3600,
        key_prefix: str = "tts",
        guild_lock_ttl_seconds: int = 30,
        completed_item_ttl_seconds: int = 900,
        telemetry: OpenTelemetryRuntime | None = None,
    ):
        self._redis = redis_client
        self._max_queue_size = max_queue_size
        self._max_queue_wait = max_queue_wait_seconds
        self._key_prefix = key_prefix
        self._guild_lock_ttl_seconds = guild_lock_ttl_seconds
        self._completed_item_ttl_seconds = completed_item_ttl_seconds
        self._telemetry = telemetry

    async def enqueue(self, item: AudioQueueItem) -> Optional[str]:
        guild_id = item.request.guild_id
        with self._telemetry.start_internal_span(
            "audio_queue.redis.enqueue",
            attributes={"guild_id": str(guild_id) if guild_id is not None else "unknown"},
        ) if self._telemetry is not None else _null_span_context() as span:
            queue_key = self._queue_key(guild_id)
            queue_size = await self._redis.llen(queue_key)
            if queue_size >= self._max_queue_size:
                logger.warning("[QUEUE] Guild %s queue full (%s items)", guild_id, self._max_queue_size)
                item.mark_failed("Fila de audio cheia. Tente novamente mais tarde.")
                await self._store_item(item)
                await self._redis.rpush(self._items_key(guild_id), item.item_id)
                span.set_attribute("result_code", "queue_full")
                return None

            item.position_in_queue = int(queue_size)
            await self._store_item(item)
            await self._redis.rpush(queue_key, item.item_id)
            await self._redis.rpush(self._items_key(guild_id), item.item_id)
            await self._redis.sadd(self._active_guilds_key(), self._guild_value(guild_id))
            await self._refresh_positions(guild_id)
            await self._record_queue_metrics(guild_id)
            logger.info("[QUEUE] Item %s enqueued to guild %s", item.item_id, guild_id)
            span.set_attribute("result_code", "enqueued")
            return item.item_id

    async def dequeue(self, guild_id: Optional[int]) -> Optional[AudioQueueItem]:
        with self._telemetry.start_internal_span(
            "audio_queue.redis.dequeue",
            attributes={"guild_id": str(guild_id) if guild_id is not None else "unknown"},
        ) if self._telemetry is not None else _null_span_context() as span:
            item_id = await self._redis.lpop(self._queue_key(guild_id))
            if item_id is None:
                await self._redis.srem(self._active_guilds_key(), self._guild_value(guild_id))
                span.set_attribute("result_code", "empty")
                await self._record_queue_metrics(guild_id)
                return None

            decoded_item_id = self._decode(item_id)
            item = await self._load_item(decoded_item_id)
            await self._refresh_positions(guild_id)
            if await self._redis.llen(self._queue_key(guild_id)) == 0:
                await self._redis.srem(self._active_guilds_key(), self._guild_value(guild_id))
            await self._record_queue_metrics(guild_id)
            span.set_attribute("result_code", "dequeued")
            return item

    async def peek_next(self, guild_id: Optional[int]) -> Optional[AudioQueueItem]:
        item_id = await self._redis.lindex(self._queue_key(guild_id), 0)
        if item_id is None:
            return None
        return await self._load_item(self._decode(item_id))

    async def get_queue_status(self, guild_id: Optional[int]) -> AudioQueueStatusDTO:
        item_ids = await self._redis.lrange(self._items_key(guild_id), 0, -1)
        items = []
        kept_ids: list[str] = []
        for raw_item_id in item_ids:
            item_id = self._decode(raw_item_id)
            item = await self._load_item(item_id)
            if item is not None:
                kept_ids.append(item_id)
                items.append(_build_status_dto(item))
        await self._rewrite_item_index(guild_id, kept_ids)
        return AudioQueueStatusDTO(size=int(await self._redis.llen(self._queue_key(guild_id))), items=items)

    async def get_item_position(self, item_id: str) -> int:
        guild_ids = await self.list_guild_ids(include_empty=True)
        for guild_id in guild_ids:
            queue_ids = await self._redis.lrange(self._queue_key(guild_id), 0, -1)
            for index, raw_item_id in enumerate(queue_ids):
                if self._decode(raw_item_id) == item_id:
                    return index
        return -1

    async def update_item(self, item: AudioQueueItem) -> None:
        ttl_seconds = None
        if item.status in (AudioQueueItemStatus.COMPLETED, AudioQueueItemStatus.FAILED):
            ttl_seconds = self._completed_item_ttl_seconds
        await self._store_item(item, ttl_seconds=ttl_seconds)

    async def clear_completed(self, guild_id: Optional[int], older_than_seconds: int = 3600):
        item_ids = await self._redis.lrange(self._items_key(guild_id), 0, -1)
        kept_ids: list[str] = []
        now = time.time()
        for raw_item_id in item_ids:
            item_id = self._decode(raw_item_id)
            item = await self._load_item(item_id)
            if item is None:
                continue
            keep = item.status in (AudioQueueItemStatus.PENDING, AudioQueueItemStatus.PROCESSING) or (
                item.completed_at and now - item.completed_at < older_than_seconds
            )
            if keep:
                kept_ids.append(item_id)
            else:
                await self._redis.delete(self._item_key(item_id))

        await self._rewrite_item_index(guild_id, kept_ids)

    async def list_guild_ids(self, include_empty: bool = False) -> list[Optional[int]]:
        guild_values = await self._redis.smembers(self._active_guilds_key())
        guild_ids = [self._guild_from_value(self._decode(value)) for value in guild_values]
        if include_empty:
            return guild_ids

        result: list[Optional[int]] = []
        for guild_id in guild_ids:
            if await self._redis.llen(self._queue_key(guild_id)) > 0:
                result.append(guild_id)
        return result

    async def acquire_guild_lock(self, guild_id: Optional[int], owner_token: str, ttl_seconds: int = 30) -> bool:
        with self._telemetry.start_internal_span(
            "audio_queue.redis.acquire_guild_lock",
            attributes={"guild_id": str(guild_id) if guild_id is not None else "unknown"},
        ) if self._telemetry is not None else _null_span_context() as span:
            ttl = ttl_seconds or self._guild_lock_ttl_seconds
            acquired = bool(await self._redis.set(self._lock_key(guild_id), owner_token, ex=ttl, nx=True))
            span.set_attribute("result_code", "acquired" if acquired else "busy")
            return acquired

    async def release_guild_lock(self, guild_id: Optional[int], owner_token: str) -> None:
        with self._telemetry.start_internal_span(
            "audio_queue.redis.release_guild_lock",
            attributes={"guild_id": str(guild_id) if guild_id is not None else "unknown"},
        ) if self._telemetry is not None else _null_span_context():
            lock_key = self._lock_key(guild_id)
            current = await self._redis.get(lock_key)
            if current is None:
                return
            if self._decode(current) == owner_token:
                await self._redis.delete(lock_key)

    async def renew_guild_lock(self, guild_id: Optional[int], owner_token: str, ttl_seconds: int = 30) -> bool:
        with self._telemetry.start_internal_span(
            "audio_queue.redis.renew_guild_lock",
            attributes={"guild_id": str(guild_id) if guild_id is not None else "unknown"},
        ) if self._telemetry is not None else _null_span_context() as span:
            lock_key = self._lock_key(guild_id)
            current = await self._redis.get(lock_key)
            if current is None or self._decode(current) != owner_token:
                span.set_attribute("result_code", "lost")
                return False
            expire = getattr(self._redis, "expire", None)
            renewed = bool(await self._redis.set(lock_key, owner_token, ex=ttl_seconds)) if expire is None else bool(
                await expire(lock_key, ttl_seconds)
            )
            span.set_attribute("result_code", "renewed" if renewed else "lost")
            return renewed

    async def aclose(self) -> None:
        close = getattr(self._redis, "aclose", None)
        if close is not None:
            await close()
            return
        close = getattr(self._redis, "close", None)
        if close is not None:
            maybe_result = close()
            if asyncio.iscoroutine(maybe_result):
                await maybe_result

    async def _store_item(self, item: AudioQueueItem, ttl_seconds: int | None = None) -> None:
        await self._redis.set(self._item_key(item.item_id), json.dumps(_item_to_payload(item)), ex=ttl_seconds)

    async def _load_item(self, item_id: str) -> Optional[AudioQueueItem]:
        payload = await self._redis.get(self._item_key(item_id))
        if payload is None:
            return None
        return _item_from_payload(json.loads(self._decode(payload)))

    async def _refresh_positions(self, guild_id: Optional[int]) -> None:
        queue_ids = await self._redis.lrange(self._queue_key(guild_id), 0, -1)
        for index, raw_item_id in enumerate(queue_ids):
            item_id = self._decode(raw_item_id)
            item = await self._load_item(item_id)
            if item is None:
                continue
            item.position_in_queue = index
            if item.status == AudioQueueItemStatus.PENDING:
                await self._store_item(item)

    async def _rewrite_item_index(self, guild_id: Optional[int], item_ids: list[str]) -> None:
        items_key = self._items_key(guild_id)
        await self._redis.delete(items_key)
        if item_ids:
            await self._redis.rpush(items_key, *item_ids)

    def _queue_key(self, guild_id: Optional[int]) -> str:
        return f"{self._key_prefix}:queue:guild:{_normalize_guild_id(guild_id)}"

    def _item_key(self, item_id: str) -> str:
        return f"{self._key_prefix}:item:{item_id}"

    def _items_key(self, guild_id: Optional[int]) -> str:
        return f"{self._key_prefix}:items:guild:{_normalize_guild_id(guild_id)}"

    def _lock_key(self, guild_id: Optional[int]) -> str:
        return f"{self._key_prefix}:lock:guild:{_normalize_guild_id(guild_id)}"

    def _processing_key(self, guild_id: Optional[int]) -> str:
        return f"{self._key_prefix}:processing:guild:{_normalize_guild_id(guild_id)}"

    def _active_guilds_key(self) -> str:
        return f"{self._key_prefix}:guilds:active"

    def _guild_value(self, guild_id: Optional[int]) -> str:
        return _normalize_guild_id(guild_id)

    def _guild_from_value(self, value: str) -> Optional[int]:
        return None if value == "noguild" else int(value)

    def _decode(self, value: Any) -> str:
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return str(value)

    async def acquire_processing_lease(
        self,
        guild_id: Optional[int],
        owner_token: str,
        ttl_seconds: int = 30,
    ) -> bool:
        with self._telemetry.start_internal_span(
            "audio_queue.redis.acquire_processing_lease",
            attributes={"guild_id": str(guild_id) if guild_id is not None else "unknown"},
        ) if self._telemetry is not None else _null_span_context() as span:
            acquired = bool(await self._redis.set(self._processing_key(guild_id), owner_token, ex=ttl_seconds, nx=True))
            span.set_attribute("result_code", "acquired" if acquired else "busy")
            return acquired

    async def release_processing_lease(self, guild_id: Optional[int], owner_token: str) -> None:
        with self._telemetry.start_internal_span(
            "audio_queue.redis.release_processing_lease",
            attributes={"guild_id": str(guild_id) if guild_id is not None else "unknown"},
        ) if self._telemetry is not None else _null_span_context():
            processing_key = self._processing_key(guild_id)
            current = await self._redis.get(processing_key)
            if current is None:
                return
            if self._decode(current) == owner_token:
                await self._redis.delete(processing_key)

    async def renew_processing_lease(
        self,
        guild_id: Optional[int],
        owner_token: str,
        ttl_seconds: int = 30,
    ) -> bool:
        with self._telemetry.start_internal_span(
            "audio_queue.redis.renew_processing_lease",
            attributes={"guild_id": str(guild_id) if guild_id is not None else "unknown"},
        ) if self._telemetry is not None else _null_span_context() as span:
            processing_key = self._processing_key(guild_id)
            current = await self._redis.get(processing_key)
            if current is None or self._decode(current) != owner_token:
                span.set_attribute("result_code", "lost")
                return False
            expire = getattr(self._redis, "expire", None)
            renewed = bool(
                await self._redis.set(processing_key, owner_token, ex=ttl_seconds)
            ) if expire is None else bool(await expire(processing_key, ttl_seconds))
            span.set_attribute("result_code", "renewed" if renewed else "lost")
            return renewed

    async def is_guild_processing(self, guild_id: Optional[int]) -> bool:
        return await self._redis.get(self._processing_key(guild_id)) is not None

    async def _record_queue_metrics(self, guild_id: Optional[int]) -> None:
        if self._telemetry is None:
            return
        queue_ids = await self._redis.lrange(self._queue_key(guild_id), 0, -1)
        self._telemetry.record_queue_depth(guild_id=guild_id, depth=len(queue_ids))
        if not queue_ids:
            return
        oldest_item = await self._load_item(self._decode(queue_ids[0]))
        if oldest_item is not None:
            self._telemetry.record_queue_age(
                guild_id=guild_id,
                age_seconds=time.time() - oldest_item.created_at,
            )


class _null_span_context:
    def __enter__(self) -> "_null_span_context":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        del exc_type, exc, tb
        return False

    def set_attribute(self, key: str, value: Any) -> None:
        del key, value
