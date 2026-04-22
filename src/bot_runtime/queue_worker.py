"""Background queue worker for Discord bot delivery."""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import Optional

from src.application.tts_queue_orchestrator import TTSQueueOrchestrator
from src.core.interfaces import IAudioQueue

logger = logging.getLogger(__name__)


class BotQueueWorker:
    """Poll queue backends and drain pending guild queues."""

    def __init__(
        self,
        *,
        audio_queue: IAudioQueue,
        queue_orchestrator: TTSQueueOrchestrator,
        poll_interval_seconds: float = 0.2,
        guild_lock_ttl_seconds: int = 30,
    ):
        self._audio_queue = audio_queue
        self._queue_orchestrator = queue_orchestrator
        self._poll_interval_seconds = poll_interval_seconds
        self._guild_lock_ttl_seconds = guild_lock_ttl_seconds
        self._worker_token = uuid.uuid4().hex
        self._runner_task: asyncio.Task | None = None
        self._guild_tasks: dict[Optional[int], asyncio.Task] = {}
        self._stop_event = asyncio.Event()

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

    async def _drain_guild(self, guild_id: Optional[int]) -> None:
        lock_acquired = False
        try:
            lock_acquired = await self._acquire_guild_lock(guild_id)
            if not lock_acquired:
                return

            while not self._stop_event.is_set():
                next_item = await self._audio_queue.peek_next(guild_id)
                if next_item is None:
                    break
                await self._queue_orchestrator.start_processing_for_item(guild_id)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("[QUEUE_WORKER] Failed while draining guild %s", guild_id)
        finally:
            self._guild_tasks.pop(guild_id, None)
            if lock_acquired:
                await self._release_guild_lock(guild_id)

    async def _list_guild_ids(self) -> list[Optional[int]]:
        list_guild_ids = getattr(self._audio_queue, "list_guild_ids", None)
        if list_guild_ids is None:
            return []
        return await list_guild_ids()

    async def _acquire_guild_lock(self, guild_id: Optional[int]) -> bool:
        acquire_guild_lock = getattr(self._audio_queue, "acquire_guild_lock", None)
        if acquire_guild_lock is None:
            return True
        return await acquire_guild_lock(guild_id, self._worker_token, ttl_seconds=self._guild_lock_ttl_seconds)

    async def _release_guild_lock(self, guild_id: Optional[int]) -> None:
        release_guild_lock = getattr(self._audio_queue, "release_guild_lock", None)
        if release_guild_lock is None:
            return
        await release_guild_lock(guild_id, self._worker_token)
