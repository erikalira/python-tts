"""Tests for bot runtime container behavior."""

import pytest
from unittest.mock import AsyncMock

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
