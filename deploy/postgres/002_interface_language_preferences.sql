CREATE TABLE IF NOT EXISTS guild_interface_language_preferences (
    guild_id BIGINT PRIMARY KEY,
    locale TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_interface_language_preferences (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    locale TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_interface_language_preferences_user_id
    ON user_interface_language_preferences (user_id);
