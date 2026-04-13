from unittest.mock import Mock

from src.bot_runtime.container import Container
from src.infrastructure.persistence.config_storage import JSONConfigStorage
from src.infrastructure.persistence.postgres_storage import PostgreSQLConfigStorage


def _build_config(backend: str):
    config = Mock()
    config.config_storage_backend = backend
    config.config_storage_dir = "configs-test"
    config.database_url = "postgresql://user:pass@localhost/db"
    return config


def test_container_uses_json_storage_when_configured():
    container = Container.__new__(Container)

    storage = container._build_config_storage(_build_config("json"))

    assert isinstance(storage, JSONConfigStorage)
    assert str(storage.storage_dir).endswith("configs-test")


def test_container_uses_postgres_storage_when_configured():
    container = Container.__new__(Container)

    storage = container._build_config_storage(_build_config("postgres"))

    assert isinstance(storage, PostgreSQLConfigStorage)
