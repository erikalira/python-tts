import asyncio

from src.core.entities import TTSConfig
from src.infrastructure.persistence.postgres_storage import PostgreSQLConfigStorage


class FakeCursor:
    def __init__(self, state):
        self._state = state

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, query, params=None):
        normalized = " ".join(query.split())
        self._state["queries"].append((normalized, params))
        if "INSERT INTO guild_tts_settings" in normalized:
            guild_id, engine, language, voice_id, rate, _settings_json = params
            self._state["guild_rows"][guild_id] = (engine, language, voice_id, rate)
        elif "INSERT INTO user_tts_settings" in normalized:
            guild_id, user_id, engine, language, voice_id, rate, _settings_json = params
            self._state["user_rows"][(guild_id, user_id)] = (engine, language, voice_id, rate)
        elif normalized.startswith("DELETE FROM guild_tts_settings"):
            guild_id = params[0]
            self._state["guild_rows"].pop(guild_id, None)
        elif normalized.startswith("DELETE FROM user_tts_settings"):
            guild_id, user_id = params
            self._state["user_rows"].pop((guild_id, user_id), None)
        elif normalized.startswith("SELECT engine, language, voice_id, rate"):
            if "FROM user_tts_settings" in normalized:
                guild_id, user_id = params
                self._state["selected"] = self._state["user_rows"].get((guild_id, user_id))
            else:
                guild_id = params[0]
                self._state["selected"] = self._state["guild_rows"].get(guild_id)

    def fetchone(self):
        return self._state.get("selected")


class FakeConnection:
    def __init__(self, state):
        self._state = state
        self.commits = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return FakeCursor(self._state)

    def commit(self):
        self.commits += 1


def test_postgres_storage_saves_and_loads_config():
    state = {"guild_rows": {}, "user_rows": {}, "queries": []}
    connection = FakeConnection(state)
    storage = PostgreSQLConfigStorage(
        database_url="postgresql://unused",
        connection_factory=lambda: connection,
    )

    config = TTSConfig(engine="edge-tts", language="pt-BR", voice_id="pt-BR-FranciscaNeural", rate=210)

    saved = asyncio.run(storage.save(123, config))
    loaded = asyncio.run(storage.load(123))

    assert saved is True
    assert loaded == config
    assert connection.commits == 1


def test_postgres_storage_deletes_config():
    state = {
        "guild_rows": {456: ("gtts", "pt", "roa/pt-br", 180)},
        "user_rows": {},
        "queries": [],
    }
    connection = FakeConnection(state)
    storage = PostgreSQLConfigStorage(
        database_url="postgresql://unused",
        connection_factory=lambda: connection,
    )

    deleted = asyncio.run(storage.delete(456))
    loaded = asyncio.run(storage.load(456))

    assert deleted is True
    assert loaded is None
    assert connection.commits == 1


def test_postgres_storage_saves_and_loads_user_config():
    state = {"guild_rows": {}, "user_rows": {}, "queries": []}
    connection = FakeConnection(state)
    storage = PostgreSQLConfigStorage(
        database_url="postgresql://unused",
        connection_factory=lambda: connection,
    )

    config = TTSConfig(engine="pyttsx3", language="system", voice_id="Maria", rate=190)

    saved = asyncio.run(storage.save(123, config, user_id=999))
    loaded = asyncio.run(storage.load(123, user_id=999))

    assert saved is True
    assert loaded == config
    assert connection.commits == 1


# pyright: reportGeneralTypeIssues=false, reportOptionalSubscript=false
