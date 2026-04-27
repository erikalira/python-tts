CREATE TABLE IF NOT EXISTS guild_tts_settings (
    guild_id BIGINT PRIMARY KEY,
    engine TEXT NOT NULL,
    language TEXT NOT NULL,
    voice_id TEXT NOT NULL,
    rate INTEGER NOT NULL,
    settings_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_tts_settings (
    guild_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    engine TEXT NOT NULL,
    language TEXT NOT NULL,
    voice_id TEXT NOT NULL,
    rate INTEGER NOT NULL,
    settings_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (guild_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_tts_settings_user_id
    ON user_tts_settings (user_id);
