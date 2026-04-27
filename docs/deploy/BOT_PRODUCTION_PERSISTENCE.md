# Bot Production Persistence

This guide documents the recommended persistence baseline for the Discord bot
when the project needs durable configuration, 24/7 availability, and room to
grow from server-scoped settings into user-level overrides.

## Recommendation

Use this baseline for production:

- `Postgres` as the durable source of truth for bot configuration
- `Docker` for packaging and consistent deploys
- `Redis` only when needed for cache, locks, or queue coordination
- JSON file storage only for local development or small single-instance testing

## Why Postgres

The bot already isolates config persistence behind `IConfigRepository`, so the
main architectural step is choosing a production-grade storage backend without
changing shared application logic.

Postgres is the preferred default because it provides:

- durable storage across restarts and redeploys
- strong consistency for settings updates
- schema migrations for future config growth
- straightforward backup and restore workflows
- clean support for both `guild` settings and future `user` overrides

## Runtime configuration

The bot runtime now supports two config storage backends:

- `CONFIG_STORAGE_BACKEND=json`
- `CONFIG_STORAGE_BACKEND=postgres`

Environment variables:

- `CONFIG_STORAGE_BACKEND`: `json` or `postgres`
- `CONFIG_STORAGE_DIR`: local directory for JSON config files
- `DATABASE_URL`: required when `CONFIG_STORAGE_BACKEND=postgres`

## Initial schema

The initial schema lives in:

- `deploy/postgres/001_bot_config_schema.sql`
- `deploy/postgres/002_interface_language_preferences.sql`

It includes:

- `guild_tts_settings`: durable per-server config
- `user_tts_settings`: durable per-user overrides inside a guild
- `guild_interface_language_preferences`: durable per-server interface language default
- `user_interface_language_preferences`: durable per-user interface language preference inside a guild

Current runtime behavior resolves voice settings in this order:

1. per-user setting in the current guild
2. guild default
3. global runtime default

Interface language is stored separately from voice settings so changing UI
language does not accidentally pin a user's inherited TTS voice. Runtime
language selection resolves in this order:

1. explicit user interface language in the current guild
2. Discord user locale from the interaction
3. explicit guild interface language
4. Discord guild locale from the interaction
5. `en-US`

## Suggested rollout

1. Keep `json` for local development if it remains convenient.
2. Provision a managed Postgres instance for production.
3. Apply the SQL files in `deploy/postgres/` in filename order.
4. Set `CONFIG_STORAGE_BACKEND=postgres` and `DATABASE_URL`.
5. Deploy the bot container with health checks and restart policy.

## Next recommended evolution

The next sensible production steps are:

1. add an explicit admin flow for changing guild defaults separately from user overrides
2. add audit or settings-history tables only if product or support workflows truly need them
3. introduce Redis only when horizontal scale or distributed coordination makes it necessary
