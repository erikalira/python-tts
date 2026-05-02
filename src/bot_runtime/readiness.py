"""Readiness checks for the Discord bot runtime."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from typing import Protocol, Self, cast

from src.application.dto import BotDependencyReadinessDTO, BotReadinessResponseDTO


class BotReadinessConfig(Protocol):
    """Configuration values needed by readiness checks."""

    config_storage_backend: str
    tts_queue_backend: str


class DiscordClientReadinessPort(Protocol):
    """Discord client readiness surface."""

    def is_ready(self) -> bool:
        """Return whether the Discord client is connected and ready."""
        ...


class QueueWorkerReadinessPort(Protocol):
    """Queue worker readiness surface."""

    def is_running(self) -> bool:
        """Return whether queue processing is active."""
        ...


class DatabaseCursorPort(Protocol):
    """Minimal DB cursor surface used by readiness pings."""

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> object:
        ...

    def execute(self, query: str) -> object:
        ...

    def fetchone(self) -> object:
        ...


class DatabaseConnectionPort(Protocol):
    """Minimal DB connection/context-manager surface."""

    def __enter__(self) -> Self:
        ...

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> object:
        ...

    def cursor(self) -> DatabaseCursorPort:
        ...


class ConfigStorageHealthPort(Protocol):
    """Storage adapter surface used for readiness pings."""

    def _connect(self) -> DatabaseConnectionPort:
        ...


class ConfigRepositoryHealthPort(Protocol):
    """Repository surface exposing its concrete storage health adapter."""

    @property
    def _storage(self) -> object:
        ...


class RedisHealthPort(Protocol):
    """Redis client surface used by readiness pings."""

    def ping(self) -> object | Awaitable[object]:
        ...


class AudioQueueHealthPort(Protocol):
    """Audio queue surface exposing the Redis client when configured."""

    _redis: RedisHealthPort | object


class BotReadinessProbe:
    """Evaluate whether the bot runtime is ready to receive production traffic."""

    def __init__(
        self,
        *,
        config: BotReadinessConfig,
        discord_client: DiscordClientReadinessPort,
        queue_worker: QueueWorkerReadinessPort,
        config_repository: ConfigRepositoryHealthPort,
        audio_queue: AudioQueueHealthPort,
    ) -> None:
        self._config = config
        self._discord_client = discord_client
        self._queue_worker = queue_worker
        self._config_repository = config_repository
        self._audio_queue = audio_queue

    async def payload(self) -> dict[str, object]:
        dependencies = [
            self._dependency(
                "discord",
                ok=self._discord_client.is_ready(),
                required=True,
                detail="client ready" if self._discord_client.is_ready() else "client not ready",
            ),
            self._dependency(
                "queue_worker",
                ok=self._queue_worker.is_running(),
                required=True,
                detail="worker running" if self._queue_worker.is_running() else "worker not running",
            ),
        ]
        dependencies.append(await self._check_config_storage())
        dependencies.append(await self._check_queue_backend())

        ready = all(dependency.status == "ready" for dependency in dependencies if dependency.required)
        response = BotReadinessResponseDTO(
            status="ready" if ready else "not_ready",
            dependencies=dependencies,
        )
        return asdict(response)

    async def _check_config_storage(self) -> BotDependencyReadinessDTO:
        if self._config.config_storage_backend != "postgres":
            return self._dependency(
                "config_storage",
                ok=True,
                required=True,
                detail=f"{self._config.config_storage_backend} backend configured",
            )

        storage = self._config_repository._storage
        connect = getattr(storage, "_connect", None)
        if not callable(connect):
            return self._dependency("postgres", ok=False, required=True, detail="connect method unavailable")
        connect_to_database = cast(Callable[[], DatabaseConnectionPort], connect)

        def _ping_postgres() -> None:
            conn = connect_to_database()
            with conn, conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()

        try:
            await asyncio.to_thread(_ping_postgres)
        except Exception as exc:
            return self._dependency("postgres", ok=False, required=True, detail=str(exc))
        return self._dependency("postgres", ok=True, required=True, detail="SELECT 1 succeeded")

    async def _check_queue_backend(self) -> BotDependencyReadinessDTO:
        if self._config.tts_queue_backend != "redis":
            return self._dependency(
                "queue_backend",
                ok=True,
                required=True,
                detail=f"{self._config.tts_queue_backend} backend configured",
            )

        redis_client = self._audio_queue._redis
        ping = getattr(redis_client, "ping", None)
        if not callable(ping):
            return self._dependency("redis", ok=False, required=True, detail="ping method unavailable")
        ping_redis = cast(Callable[[], object | Awaitable[object]], ping)

        try:
            result = ping_redis()
            if asyncio.iscoroutine(result):
                result = await result
        except Exception as exc:
            return self._dependency("redis", ok=False, required=True, detail=str(exc))
        return self._dependency("redis", ok=bool(result), required=True, detail=f"ping returned {result!r}")

    def _dependency(
        self,
        name: str,
        *,
        ok: bool,
        required: bool,
        detail: str | None = None,
    ) -> BotDependencyReadinessDTO:
        return BotDependencyReadinessDTO(
            name=name,
            status="ready" if ok else "not_ready",
            required=required,
            detail=detail,
        )
