"""Unit tests for config file."""

from src.core.config import configuration


class TestSettings:
    def test_ok(self):
        assert str(configuration.SQL_DB.psql_url) == (
            "postgresql+asyncpg://dbuser:dbpass@localhost:5432/postgres"
        )
        assert configuration.VECTOR_DB.HOST == "localhost"
        assert configuration.VECTOR_DB.KEY == "secret-db-key"
        assert configuration.DROPBOX.CLIENT_ID == "dropbox-client-id"
        assert configuration.DROPBOX.CLIENT_SECRET == "dropbox-client-secret"
        assert configuration.COHERE_API_KEY == "cohere-api-key"
