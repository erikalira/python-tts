"""Background queue worker for Discord bot delivery."""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Protocol

from src.application.dto import SpeakTextResult
from src.core.interfaces import IAudioQueue
from src.infrastructure.opentelemetry_runtime import OpenTelemetryRuntime

logger = logging.getLogger(__name__)


class QueueOrchestratorPort(Protocol):
    """Minimal queue orchestrator behavior needed by the worker."""

    async def start_processing_for_item(self, guild_id: int | None) -> SpeakTextResult:
        """Process the next item for a guild."""
        ...


def _default_lock_renew_interval_seconds(ttl_seconds: float) -> float:
    """Return a safe renew cadence for distributed locks and leases."""

    return max(0.1, ttl_seconds / 3)


class BotQueueWorker:
    """Poll queue backends and drain pending guild queues."""

    def __init__(
        self,
        *,
        audio_queue: IAudioQueue,
        queue_orchestrator: QueueOrchestratorPort,
        poll_interval_seconds: float = 0.2,
        guild_lock_ttl_seconds: int = 30,
        guild_lock_renew_interval_seconds: float | None = None,
        processing_lease_ttl_seconds: int | None = None,
        processing_lease_renew_interval_seconds: float | None = None,
        otel_runtime: OpenTelemetryRuntime | None = None,
    ):
        self._audio_queue = audio_queue
        self._queue_orchestrator = queue_orchestrator
        self._poll_interval_seconds = poll_interval_seconds
        self._guild_lock_ttl_seconds = guild_lock_ttl_seconds
        self._guild_lock_renew_interval_seconds = (
            guild_lock_renew_interval_seconds
            if guild_lock_renew_interval_seconds is not None
            else _default_lock_renew_interval_seconds(guild_lock_ttl_seconds)
        )
        self._processing_lease_ttl_seconds = (
            processing_lease_ttl_seconds if processing_lease_ttl_seconds is not None else guild_lock_ttl_seconds
        )
        self._processing_lease_renew_interval_seconds = (
            processing_lease_renew_interval_seconds
            if processing_lease_renew_interval_seconds is not None
            else _default_lock_renew_interval_seconds(self._processing_lease_ttl_seconds)
        )
        self._worker_token = uuid.uuid4().hex
        self._runner_task: asyncio.Task | None = None
        self._guild_tasks: dict[int | None, asyncio.Task] = {}
        self._stop_event = asyncio.Event()
        self._otel_runtime = otel_runtime

    async def start(self) -> None:
        if self._runner_task and not self._runner_task.done():
            return
        self._stop_event.clear()
        self._runner_task = asyncio.create_task(self._run(), name="discord-bot-queue-worker")

    def is_running(self) -> bool:
        return self._runner_task is not None and not self._runner_task.done()

    async def stop(self) -> None:
        self._stop_event.set()
        tasks = [task for task in self._guild_tasks.values() if not task.done()]
        if self._runner_task and not self._runner_task.done():
            self._runner_task.cancel()
            tasks.append(self._runner_task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._guild_tasks.clear()
        self._runner_task = None

    async def _run(self) -> None:
        try:
            while not self._stop_event.is_set():
                with (
                    self._otel_runtime.start_internal_span("queue_worker.poll")
                    if self._otel_runtime is not None
                    else _null_span_context()
                ):
                    guild_ids = await self._list_guild_ids()
                for guild_id in guild_ids:
                    task = self._guild_tasks.get(guild_id)
                    if task and not task.done():
                        continue
                    self._guild_tasks[guild_id] = asyncio.create_task(
                        self._drain_guild(guild_id),
                        name=f"discord-bot-queue-guild-{guild_id}",
                    )
                await asyncio.sleep(self._poll_interval_seconds)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[QUEUE_WORKER] Unhandled queue worker failure")

    async def _drain_guild(self, guild_id: int | None) -> None:
        lock_acquired = False
        renew_task: asyncio.Task | None = None
        try:
            lock_acquired = await self._acquire_guild_lock(guild_id)
            if not lock_acquired:
                return
            renew_task = asyncio.create_task(
                self._renew_guild_lock_loop(guild_id),
                name=f"discord-bot-queue-lock-renew-{guild_id}",
            )

            while not self._stop_event.is_set():
                next_item = await self._audio_queue.peek_next(guild_id)
                if next_item is None:
                    break
                with (
                    self._otel_runtime.start_consumer_span(
                        "queue_worker.process_guild_item",
                        carrier=next_item.trace_context,
                        attributes={
                            "guild_id": str(guild_id) if guild_id is not None else "unknown",
                            "engine": self._resolve_engine_name(next_item),
                        },
                    )
                    if self._otel_runtime is not None
                    else _null_span_context() as span
                ):
                    processing_acquired = await self._acquire_processing_lease(guild_id)
                    if not processing_acquired:
                        logger.debug("[QUEUE_WORKER] Guild %s already has an active processing lease", guild_id)
                        span.set_attribute("result_code", "lease_busy")
                        break
                    processing_renew_task = asyncio.create_task(
                        self._renew_processing_lease_loop(guild_id),
                        name=f"discord-bot-processing-lease-renew-{guild_id}",
                    )
                    try:
                        result = await self._queue_orchestrator.start_processing_for_item(guild_id)
                        span.set_attribute("result_code", result.code)
                        span.set_attribute("timeout_flag", result.code in {"generation_timeout", "playback_timeout"})
                    finally:
                        processing_renew_task.cancel()
                        await asyncio.gather(processing_renew_task, return_exceptions=True)
                        await self._release_processing_lease(guild_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[QUEUE_WORKER] Failed while draining guild %s", guild_id)
        finally:
            if renew_task is not None:
                renew_task.cancel()
                await asyncio.gather(renew_task, return_exceptions=True)
            self._guild_tasks.pop(guild_id, None)
            if lock_acquired:
                await self._release_guild_lock(guild_id)

    async def _list_guild_ids(self) -> list[int | None]:
        list_guild_ids = getattr(self._audio_queue, "list_guild_ids", None)
        if list_guild_ids is None:
            return []
        return await list_guild_ids()

    async def _acquire_guild_lock(self, guild_id: int | None) -> bool:
        acquire_guild_lock = getattr(self._audio_queue, "acquire_guild_lock", None)
        if acquire_guild_lock is None:
            return True
        return await acquire_guild_lock(guild_id, self._worker_token, ttl_seconds=self._guild_lock_ttl_seconds)

    async def _release_guild_lock(self, guild_id: int | None) -> None:
        release_guild_lock = getattr(self._audio_queue, "release_guild_lock", None)
        if release_guild_lock is None:
            return
        await release_guild_lock(guild_id, self._worker_token)

    async def _renew_guild_lock_loop(self, guild_id: int | None) -> None:
        renew_guild_lock = getattr(self._audio_queue, "renew_guild_lock", None)
        if renew_guild_lock is None:
            return

        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(self._guild_lock_renew_interval_seconds)
                renewed = await renew_guild_lock(
                    guild_id,
                    self._worker_token,
                    ttl_seconds=self._guild_lock_ttl_seconds,
                )
                if not renewed:
                    logger.warning("[QUEUE_WORKER] Lost guild lock while draining guild %s", guild_id)
                    if self._otel_runtime is not None:
                        self._otel_runtime.record_lock_loss(guild_id=guild_id, lock_kind="guild_lock")
                    return
        except asyncio.CancelledError:
            raise

    async def _acquire_processing_lease(self, guild_id: int | None) -> bool:
        return await self._audio_queue.acquire_processing_lease(
            guild_id,
            self._worker_token,
            ttl_seconds=self._processing_lease_ttl_seconds,
        )

    async def _release_processing_lease(self, guild_id: int | None) -> None:
        await self._audio_queue.release_processing_lease(guild_id, self._worker_token)

    async def _renew_processing_lease_loop(self, guild_id: int | None) -> None:
        try:
            while not self._stop_event.is_set():
                await asyncio.sleep(self._processing_lease_renew_interval_seconds)
                renewed = await self._audio_queue.renew_processing_lease(
                    guild_id,
                    self._worker_token,
                    ttl_seconds=self._processing_lease_ttl_seconds,
                )
                if not renewed:
                    logger.warning("[QUEUE_WORKER] Lost processing lease while handling guild %s", guild_id)
                    if self._otel_runtime is not None:
                        self._otel_runtime.record_lock_loss(guild_id=guild_id, lock_kind="processing_lease")
                    return
        except asyncio.CancelledError:
            raise

    def _resolve_engine_name(self, item) -> str:
        override = item.request.config_override
        if override is not None and override.engine:
            return override.engine
        return "configured_default"


class _null_span_context:
    def __enter__(self) -> _null_span_context:
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        del exc_type, exc, tb
        return False

    def set_attribute(self, key: str, value) -> None:
        del key, value
