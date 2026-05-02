"""Postgres-backed configuration persistence for Discord bot settings."""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

from src.core.entities import TTSConfig

from .config_storage import IConfigStorage

logger = logging.getLogger(__name__)

try:  # pragma: no cover - import availability is validated through behavior
    import psycopg
except ImportError:  # pragma: no cover - exercised via backend validation paths
    psycopg = None


class PostgreSQLConfigStorage(IConfigStorage):
    """Persist guild-scoped config in Postgres with room for future growth."""

    def __init__(
        self,
        database_url: str,
        connection_factory: Callable[[], Any] | None = None,
    ):
        self._database_url = database_url
        self._connection_factory = connection_factory

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()

        if psycopg is None:
            raise RuntimeError("Postgres config storage requires the optional 'psycopg' dependency.")

        return psycopg.connect(self._database_url)

    def load_sync(self, guild_id: int, user_id: int | None = None) -> TTSConfig | None:
        try:
            with self._connect() as conn, conn.cursor() as cursor:
                if user_id is not None:
                    cursor.execute(
                        """
                            SELECT engine, language, voice_id, rate
                            FROM user_tts_settings
                            WHERE guild_id = %s AND user_id = %s
                            """,
                        (guild_id, user_id),
                    )
                else:
                    cursor.execute(
                        """
                            SELECT engine, language, voice_id, rate
                            FROM guild_tts_settings
                            WHERE guild_id = %s
                            """,
                        (guild_id,),
                    )
                row = cursor.fetchone()
        except Exception as exc:
            logger.error(
                "[POSTGRES_CONFIG_STORAGE] Failed to load config synchronously for guild %s: %s", guild_id, exc
            )
            return None

        if row is None:
            return None

        engine, language, voice_id, rate = row
        return TTSConfig(engine=engine, language=language, voice_id=voice_id, rate=rate)

    async def load(self, guild_id: int, user_id: int | None = None) -> TTSConfig | None:
        return self.load_sync(guild_id, user_id=user_id)

    async def save(self, guild_id: int, config: TTSConfig, user_id: int | None = None) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    settings_json = json.dumps(
                        {
                            "engine": config.engine,
                            "language": config.language,
                            "voice_id": config.voice_id,
                            "rate": config.rate,
                        }
                    )
                    if user_id is not None:
                        cursor.execute(
                            """
                            INSERT INTO user_tts_settings (guild_id, user_id, engine, language, voice_id, rate, settings_json)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (guild_id, user_id)
                            DO UPDATE SET
                                engine = EXCLUDED.engine,
                                language = EXCLUDED.language,
                                voice_id = EXCLUDED.voice_id,
                                rate = EXCLUDED.rate,
                                settings_json = EXCLUDED.settings_json,
                                updated_at = NOW()
                            """,
                            (
                                guild_id,
                                user_id,
                                config.engine,
                                config.language,
                                config.voice_id,
                                config.rate,
                                settings_json,
                            ),
                        )
                    else:
                        cursor.execute(
                            """
                            INSERT INTO guild_tts_settings (guild_id, engine, language, voice_id, rate, settings_json)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (guild_id)
                            DO UPDATE SET
                                engine = EXCLUDED.engine,
                                language = EXCLUDED.language,
                                voice_id = EXCLUDED.voice_id,
                                rate = EXCLUDED.rate,
                                settings_json = EXCLUDED.settings_json,
                                updated_at = NOW()
                            """,
                            (
                                guild_id,
                                config.engine,
                                config.language,
                                config.voice_id,
                                config.rate,
                                settings_json,
                            ),
                        )
                conn.commit()
        except Exception as exc:
            logger.error("[POSTGRES_CONFIG_STORAGE] Failed to save config for guild %s: %s", guild_id, exc)
            return False

        return True

    async def delete(self, guild_id: int, user_id: int | None = None) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    if user_id is not None:
                        cursor.execute(
                            "DELETE FROM user_tts_settings WHERE guild_id = %s AND user_id = %s",
                            (guild_id, user_id),
                        )
                    else:
                        cursor.execute("DELETE FROM guild_tts_settings WHERE guild_id = %s", (guild_id,))
                conn.commit()
        except Exception as exc:
            logger.error("[POSTGRES_CONFIG_STORAGE] Failed to delete config for guild %s: %s", guild_id, exc)
            return False

        return True
