"""Migrate guild config files from JSON storage into Postgres."""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from src.infrastructure.persistence.config_storage import JSONConfigStorage
from src.infrastructure.persistence.postgres_storage import PostgreSQLConfigStorage

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


async def migrate(storage_dir: str, database_url: str) -> int:
    source = JSONConfigStorage(storage_dir=storage_dir)
    target = PostgreSQLConfigStorage(database_url=database_url)
    migrated = 0

    for config_file in sorted(Path(storage_dir).glob("guild_*.json")):
        stem_parts = config_file.stem.split("_")
        if len(stem_parts) < 2 or stem_parts[0] != "guild" or not stem_parts[1].isdigit():
            logger.warning("Skipping unexpected config file: %s", config_file.name)
            continue

        guild_id = int(stem_parts[1])
        user_id = None
        if len(stem_parts) == 4 and stem_parts[2] == "user" and stem_parts[3].isdigit():
            user_id = int(stem_parts[3])
        elif len(stem_parts) != 2:
            logger.warning("Skipping unexpected config file: %s", config_file.name)
            continue

        config = await source.load(guild_id, user_id=user_id)
        if config is None:
            logger.warning(
                "Skipping guild %s user %s because the config could not be loaded",
                guild_id,
                user_id,
            )
            continue

        saved = await target.save(guild_id, config, user_id=user_id)
        if not saved:
            raise RuntimeError(f"Failed to migrate guild {guild_id} user {user_id}")

        migrated += 1
        if user_id is None:
            logger.info("Migrated guild %s", guild_id)
        else:
            logger.info("Migrated guild %s user %s", guild_id, user_id)

    return migrated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage-dir", default="configs", help="Directory containing guild_*.json files")
    parser.add_argument("--database-url", required=True, help="Postgres DATABASE_URL")
    args = parser.parse_args()

    migrated = asyncio.run(migrate(storage_dir=args.storage_dir, database_url=args.database_url))
    logger.info("Migration complete. Migrated %s guild config(s).", migrated)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
