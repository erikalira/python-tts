"""Readiness checks for the Discord bot runtime."""

from __future__ import annotations

import asyncio
from dataclasses import asdict
from typing import Any

from src.application.dto import BotDependencyReadinessDTO, BotReadinessResponseDTO


class BotReadinessProbe:
    """Evaluate whether the bot runtime is ready to receive production traffic."""

    def __init__(
        self,
        *,
        config: Any,
        discord_client: Any,
        queue_worker: Any,
        config_repository: Any,
        audio_queue: Any,
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

        storage = getattr(self._config_repository, "_storage", None)
        connect = getattr(storage, "_connect", None)
        if not callable(connect):
            return self._dependency("postgres", ok=False, required=True, detail="connect method unavailable")

        def _ping_postgres() -> None:
            conn: Any = connect()
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

        redis_client = getattr(self._audio_queue, "_redis", None)
        ping = getattr(redis_client, "ping", None)
        if not callable(ping):
            return self._dependency("redis", ok=False, required=True, detail="ping method unavailable")

        try:
            result = ping()
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
