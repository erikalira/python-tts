"""Tests for bot runtime container behavior."""

from unittest.mock import AsyncMock, Mock

import pytest

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

    async def test_shutdown_flushes_otel_runtime_when_available(self):
        container = Container.__new__(Container)
        container.queue_worker = type("Worker", (), {})()
        container.queue_worker.stop = AsyncMock()
        container.queue_worker.is_running = Mock(return_value=False)
        container.audio_queue = type("Queue", (), {})()
        container.audio_queue.aclose = AsyncMock()
        container.otel_runtime = type("OTel", (), {})()
        container.otel_runtime.shutdown = Mock()

        await Container.shutdown(container)

        container.audio_queue.aclose.assert_awaited_once()
        container.otel_runtime.shutdown.assert_called_once_with()

    async def test_start_queue_worker_restarts_when_previous_runner_died(self):
        container = Container.__new__(Container)
        container.queue_worker = type("Worker", (), {})()
        container.queue_worker.start = AsyncMock()
        container.queue_worker.is_running = Mock(side_effect=[False, False])

        await Container._start_queue_worker_once(container)
        await Container._start_queue_worker_once(container)

        assert container.queue_worker.start.await_count == 2


def _write_env(tmp_path, extra: list[str] | None = None):
    lines = [
        "DISCORD_TOKEN=test-token",
        f"CONFIG_STORAGE_DIR={tmp_path / 'configs'}",
        "CONFIG_STORAGE_BACKEND=json",
        "TTS_QUEUE_BACKEND=inmemory",
        *(extra or []),
    ]
    env_file = tmp_path / ".env"
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return env_file


class TestContainerWiring:
    """Build a real Container and assert what __init__ actually hands over.

    The per-helper tests prove each builder in isolation; only constructing the
    container proves __init__ passes their results to the collaborators that
    need them. A dropped keyword there leaves every helper test green.
    """

    def test_fish_audio_settings_reach_the_routed_engine(self, tmp_path):
        from src.bot_runtime.settings import Config
        from src.infrastructure.tts.engines import FishAudioSettings

        config = Config(env_file=_write_env(tmp_path, ["FISH_AUDIO=fish-key", "FISH_AUDIO_MODEL=s2.1-pro"]))
        container = Container(config)

        assert container.tts_engine._fish_audio == FishAudioSettings(api_key="fish-key", model="s2.1-pro")

    def test_no_fish_settings_when_no_key_is_configured(self, tmp_path):
        from src.bot_runtime.settings import Config

        container = Container(Config(env_file=_write_env(tmp_path)))

        assert container.tts_engine._fish_audio is None

    def test_container_warns_about_third_party_retention(self, tmp_path, caplog):
        """An operator must not be able to enable this engine silently."""
        import logging

        from src.bot_runtime.settings import Config

        config = Config(env_file=_write_env(tmp_path, ["FISH_AUDIO=fish-key"]))
        with caplog.at_level(logging.WARNING):
            Container(config)

        assert "retain" in caplog.text.lower()
        assert "fish-key" not in caplog.text

    def test_security_relevant_settings_reach_their_collaborators(self, tmp_path):
        """The constructor can drop these silently, and nothing else notices.

        All three kwargs have permissive defaults (None, None, 500), so cutting
        one raises no TypeError. Dropping `auth_token` leaves HTTP /speak
        unauthenticated in production; mutation testing confirmed the whole
        suite stayed green through exactly that cut. Six `is not None` checks
        proved only that the attribute names exist, which no realistic bug
        produces on its own.
        """
        from src.bot_runtime.settings import Config

        config = Config(
            env_file=_write_env(
                tmp_path,
                [
                    "BOT_SPEAK_TOKEN=http-secret",
                    "MAX_TEXT_LENGTH=321",
                    "BOT_RATE_LIMIT_MAX_REQUESTS=5",
                ],
            )
        )
        container = Container(config)

        assert container.speak_controller._auth_token == "http-secret"
        assert container.speak_controller._rate_limiter is container.rate_limiter
        assert container.speak_controller._rate_limit_max_requests == 5
        assert container.speak_controller._max_text_length == 321
        assert container.speak_use_case._max_text_length == 321
