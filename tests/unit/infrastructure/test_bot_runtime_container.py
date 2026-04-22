"""Tests for bot runtime container behavior."""

import pytest
from unittest.mock import AsyncMock, Mock

from src.bot_runtime.container import Container


@pytest.mark.asyncio
class TestContainer:
    async def test_sync_commands_once_only_calls_sync_on_first_attempt(self):
        container = Container.__new__(Container)
        container._commands_synced = False
        container.command_tree = type("Tree", (), {})()
        container.command_tree.sync = AsyncMock()

        await Container._sync_commands_once(container)
        await Container._sync_commands_once(container)

        container.command_tree.sync.assert_awaited_once()
        assert container._commands_synced is True

    async def test_sync_commands_once_does_not_mark_synced_on_failure(self):
        container = Container.__new__(Container)
        container._commands_synced = False
        container.command_tree = type("Tree", (), {})()
        container.command_tree.sync = AsyncMock(side_effect=RuntimeError("boom"))

        await Container._sync_commands_once(container)

        assert container._commands_synced is False

    async def test_start_queue_worker_once_only_runs_single_time(self):
        container = Container.__new__(Container)
        container.queue_worker = type("Worker", (), {})()
        container.queue_worker.start = AsyncMock()
        container.queue_worker.is_running = Mock(side_effect=[False, True])

        await Container._start_queue_worker_once(container)
        await Container._start_queue_worker_once(container)

        container.queue_worker.start.assert_awaited_once()

    async def test_shutdown_only_stops_queue_worker_after_start(self):
        container = Container.__new__(Container)
        container.queue_worker = type("Worker", (), {})()
        container.queue_worker.stop = AsyncMock()
        container.queue_worker.is_running = Mock(return_value=True)
        container.audio_queue = type("Queue", (), {})()
        container.audio_queue.aclose = AsyncMock()

        await Container.shutdown(container)

        container.queue_worker.stop.assert_awaited_once()
        container.audio_queue.aclose.assert_awaited_once()

    async def test_start_queue_worker_restarts_when_previous_runner_died(self):
        container = Container.__new__(Container)
        container.queue_worker = type("Worker", (), {})()
        container.queue_worker.start = AsyncMock()
        container.queue_worker.is_running = Mock(side_effect=[False, False])

        await Container._start_queue_worker_once(container)
        await Container._start_queue_worker_once(container)

        assert container.queue_worker.start.await_count == 2
