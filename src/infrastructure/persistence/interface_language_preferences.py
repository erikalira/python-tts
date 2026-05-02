"""Persistence adapters for Discord interface language preferences."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Optional
from collections.abc import Callable

logger = logging.getLogger(__name__)

try:  # pragma: no cover - import availability is validated through behavior
    import psycopg
except ImportError:  # pragma: no cover - exercised via backend validation paths
    psycopg = None


class JSONInterfaceLanguagePreferenceRepository:
    """Store interface language preferences in JSON files with negative caching."""

    def __init__(self, storage_dir: str = "configs"):
        self._storage_dir = Path(storage_dir)
        self._storage_dir.mkdir(exist_ok=True)
        self._guild_cache: dict[int, str | None] = {}
        self._user_cache: dict[tuple[int, int], str | None] = {}

    def _guild_path(self, guild_id: int) -> Path:
        return self._storage_dir / f"guild_{guild_id}_interface_language.json"

    def _user_path(self, guild_id: int, user_id: int) -> Path:
        return self._storage_dir / f"guild_{guild_id}_user_{user_id}_interface_language.json"

    def _load(self, path: Path) -> str | None:
        if not path.exists():
            return None

        try:
            with open(path, encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError) as exc:
            logger.error("[INTERFACE_LANGUAGE] Failed to load %s: %s", path, exc)
            return None

        locale = data.get("locale")
        return str(locale) if locale else None

    def _save(self, path: Path, payload: dict[str, object]) -> bool:
        try:
            with open(path, "w", encoding="utf-8") as file:
                json.dump(payload, file, indent=2)
        except OSError as exc:
            logger.error("[INTERFACE_LANGUAGE] Failed to save %s: %s", path, exc)
            return False
        return True

    def get_user_language(self, guild_id: int, user_id: int) -> Optional[str]:
        cache_key = (guild_id, user_id)
        if cache_key not in self._user_cache:
            self._user_cache[cache_key] = self._load(self._user_path(guild_id, user_id))
        return self._user_cache[cache_key]

    def get_guild_language(self, guild_id: int) -> Optional[str]:
        if guild_id not in self._guild_cache:
            self._guild_cache[guild_id] = self._load(self._guild_path(guild_id))
        return self._guild_cache[guild_id]

    async def set_user_language(self, guild_id: int, user_id: int, locale: str) -> bool:
        saved = self._save(
            self._user_path(guild_id, user_id),
            {"guild_id": guild_id, "user_id": user_id, "locale": locale},
        )
        if saved:
            self._user_cache[(guild_id, user_id)] = locale
        return saved

    async def set_guild_language(self, guild_id: int, locale: str) -> bool:
        saved = self._save(self._guild_path(guild_id), {"guild_id": guild_id, "locale": locale})
        if saved:
            self._guild_cache[guild_id] = locale
        return saved

    async def delete_user_language(self, guild_id: int, user_id: int) -> bool:
        path = self._user_path(guild_id, user_id)
        try:
            if path.exists():
                path.unlink()
        except OSError as exc:
            logger.error("[INTERFACE_LANGUAGE] Failed to delete %s: %s", path, exc)
            return False
        self._user_cache[(guild_id, user_id)] = None
        return True

    async def delete_guild_language(self, guild_id: int) -> bool:
        path = self._guild_path(guild_id)
        try:
            if path.exists():
                path.unlink()
        except OSError as exc:
            logger.error("[INTERFACE_LANGUAGE] Failed to delete %s: %s", path, exc)
            return False
        self._guild_cache[guild_id] = None
        return True


class PostgreSQLInterfaceLanguagePreferenceRepository:
    """Store interface language preferences in Postgres with negative caching."""

    def __init__(
        self,
        database_url: str,
        connection_factory: Optional[Callable[[], Any]] = None,
    ):
        self._database_url = database_url
        self._connection_factory = connection_factory
        self._guild_cache: dict[int, str | None] = {}
        self._user_cache: dict[tuple[int, int], str | None] = {}

    def _connect(self) -> Any:
        if self._connection_factory is not None:
            return self._connection_factory()

        if psycopg is None:
            raise RuntimeError(
                "Postgres interface language storage requires the optional 'psycopg' dependency."
            )

        return psycopg.connect(self._database_url)

    def get_user_language(self, guild_id: int, user_id: int) -> Optional[str]:
        cache_key = (guild_id, user_id)
        if cache_key in self._user_cache:
            return self._user_cache[cache_key]

        try:
            with self._connect() as conn, conn.cursor() as cursor:
                cursor.execute(
                    """
                        SELECT locale
                        FROM user_interface_language_preferences
                        WHERE guild_id = %s AND user_id = %s
                        """,
                    (guild_id, user_id),
                )
                row = cursor.fetchone()
        except Exception as exc:
            logger.error(
                "[INTERFACE_LANGUAGE] Failed to load user locale for guild %s user %s: %s",
                guild_id,
                user_id,
                exc,
            )
            return None

        self._user_cache[cache_key] = str(row[0]) if row else None
        return self._user_cache[cache_key]

    def get_guild_language(self, guild_id: int) -> Optional[str]:
        if guild_id in self._guild_cache:
            return self._guild_cache[guild_id]

        try:
            with self._connect() as conn, conn.cursor() as cursor:
                cursor.execute(
                    """
                        SELECT locale
                        FROM guild_interface_language_preferences
                        WHERE guild_id = %s
                        """,
                    (guild_id,),
                )
                row = cursor.fetchone()
        except Exception as exc:
            logger.error("[INTERFACE_LANGUAGE] Failed to load guild locale for guild %s: %s", guild_id, exc)
            return None

        self._guild_cache[guild_id] = str(row[0]) if row else None
        return self._guild_cache[guild_id]

    async def set_user_language(self, guild_id: int, user_id: int, locale: str) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO user_interface_language_preferences (guild_id, user_id, locale)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (guild_id, user_id)
                        DO UPDATE SET locale = EXCLUDED.locale, updated_at = NOW()
                        """,
                        (guild_id, user_id, locale),
                    )
                conn.commit()
        except Exception as exc:
            logger.error(
                "[INTERFACE_LANGUAGE] Failed to save user locale for guild %s user %s: %s",
                guild_id,
                user_id,
                exc,
            )
            return False

        self._user_cache[(guild_id, user_id)] = locale
        return True

    async def set_guild_language(self, guild_id: int, locale: str) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO guild_interface_language_preferences (guild_id, locale)
                        VALUES (%s, %s)
                        ON CONFLICT (guild_id)
                        DO UPDATE SET locale = EXCLUDED.locale, updated_at = NOW()
                        """,
                        (guild_id, locale),
                    )
                conn.commit()
        except Exception as exc:
            logger.error("[INTERFACE_LANGUAGE] Failed to save guild locale for guild %s: %s", guild_id, exc)
            return False

        self._guild_cache[guild_id] = locale
        return True

    async def delete_user_language(self, guild_id: int, user_id: int) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        """
                        DELETE FROM user_interface_language_preferences
                        WHERE guild_id = %s AND user_id = %s
                        """,
                        (guild_id, user_id),
                    )
                conn.commit()
        except Exception as exc:
            logger.error(
                "[INTERFACE_LANGUAGE] Failed to delete user locale for guild %s user %s: %s",
                guild_id,
                user_id,
                exc,
            )
            return False

        self._user_cache[(guild_id, user_id)] = None
        return True

    async def delete_guild_language(self, guild_id: int) -> bool:
        try:
            with self._connect() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM guild_interface_language_preferences WHERE guild_id = %s",
                        (guild_id,),
                    )
                conn.commit()
        except Exception as exc:
            logger.error("[INTERFACE_LANGUAGE] Failed to delete guild locale for guild %s: %s", guild_id, exc)
            return False

        self._guild_cache[guild_id] = None
        return True
