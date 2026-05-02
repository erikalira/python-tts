import asyncio

from src.infrastructure.persistence.interface_language_preferences import (
    JSONInterfaceLanguagePreferenceRepository,
    PostgreSQLInterfaceLanguagePreferenceRepository,
)


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
        if "INSERT INTO guild_interface_language_preferences" in normalized:
            guild_id, locale = params
            self._state["guild_rows"][guild_id] = locale
        elif "INSERT INTO user_interface_language_preferences" in normalized:
            guild_id, user_id, locale = params
            self._state["user_rows"][(guild_id, user_id)] = locale
        elif normalized.startswith("DELETE FROM guild_interface_language_preferences"):
            guild_id = params[0]
            self._state["guild_rows"].pop(guild_id, None)
        elif normalized.startswith("DELETE FROM user_interface_language_preferences"):
            guild_id, user_id = params
            self._state["user_rows"].pop((guild_id, user_id), None)
        elif normalized.startswith("SELECT locale"):
            if "FROM user_interface_language_preferences" in normalized:
                guild_id, user_id = params
                locale = self._state["user_rows"].get((guild_id, user_id))
            else:
                guild_id = params[0]
                locale = self._state["guild_rows"].get(guild_id)
            self._state["selected"] = (locale,) if locale else None

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


class FailingConnection:
    def __enter__(self):
        raise RuntimeError("temporary database outage")

    def __exit__(self, exc_type, exc, tb):
        return False


def test_json_interface_language_preferences_save_load_and_delete(tmp_path):
    repository = JSONInterfaceLanguagePreferenceRepository(storage_dir=str(tmp_path))

    assert asyncio.run(repository.set_user_language(123, 999, "pt-BR")) is True
    assert asyncio.run(repository.set_guild_language(123, "en-US")) is True

    assert repository.get_user_language(123, 999) == "pt-BR"
    assert repository.get_guild_language(123) == "en-US"

    assert asyncio.run(repository.delete_user_language(123, 999)) is True
    assert asyncio.run(repository.delete_guild_language(123)) is True

    assert repository.get_user_language(123, 999) is None
    assert repository.get_guild_language(123) is None


def test_postgres_interface_language_preferences_save_load_and_delete():
    state = {"guild_rows": {}, "user_rows": {}, "queries": []}
    connection = FakeConnection(state)
    repository = PostgreSQLInterfaceLanguagePreferenceRepository(
        database_url="postgresql://unused",
        connection_factory=lambda: connection,
    )

    assert asyncio.run(repository.set_user_language(123, 999, "pt-BR")) is True
    assert asyncio.run(repository.set_guild_language(123, "en-US")) is True

    assert repository.get_user_language(123, 999) == "pt-BR"
    assert repository.get_guild_language(123) == "en-US"

    assert asyncio.run(repository.delete_user_language(123, 999)) is True
    assert asyncio.run(repository.delete_guild_language(123)) is True

    assert repository.get_user_language(123, 999) is None
    assert repository.get_guild_language(123) is None
    assert connection.commits == 4


def test_postgres_user_language_read_exception_does_not_cache_missing_locale():
    state = {"guild_rows": {}, "user_rows": {(123, 999): "pt-BR"}, "queries": []}
    attempts = iter([FailingConnection(), FakeConnection(state)])
    repository = PostgreSQLInterfaceLanguagePreferenceRepository(
        database_url="postgresql://unused",
        connection_factory=lambda: next(attempts),
    )

    assert repository.get_user_language(123, 999) is None
    assert repository.get_user_language(123, 999) == "pt-BR"


def test_postgres_guild_language_read_exception_does_not_cache_missing_locale():
    state = {"guild_rows": {123: "en-US"}, "user_rows": {}, "queries": []}
    attempts = iter([FailingConnection(), FakeConnection(state)])
    repository = PostgreSQLInterfaceLanguagePreferenceRepository(
        database_url="postgresql://unused",
        connection_factory=lambda: next(attempts),
    )

    assert repository.get_guild_language(123) is None
    assert repository.get_guild_language(123) == "en-US"
# pyright: reportGeneralTypeIssues=false, reportOptionalSubscript=false
