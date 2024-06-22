"""Project configurations."""

from pydantic import BaseModel, PostgresDsn, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class SqlDBConfigurations(BaseModel):
    """Sql DB configurations class.

    Attributes:
        HOST: Database host
        PORT: Database port.
        USER: Database user.
        PASSWORD: Database password.
        NAME: Database name.
    """

    HOST: str
    PORT: int
    USER: str
    PASSWORD: str
    NAME: str

    @computed_field
    def psql_url(self) -> PostgresDsn:
        """Generate database URL.

        Returns:
                Database URL.
        """
        return MultiHostUrl.build(
            scheme="postgresql+asyncpg",
            username=self.USER,
            password=self.PASSWORD,
            host=self.HOST,
            path=self.NAME,
            port=self.PORT,
        )


class VectorDBConfigurations(BaseModel):
    """Vector DB configurations class.

    Attributes:
        HOST: Database host.
        KEY: Database key.
    """

    HOST: str
    KEY: str


class DropboxConfigurations(BaseModel):
    """Dropbox configurations class.

    Attributes:
        CLIENT_ID: Dropbox client ID.
        CLIENT_SECRET: Dropbox client secret.
    """

    CLIENT_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str


class Configuration(BaseSettings):
    """Project settings class."""

    model_config = SettingsConfigDict(env_nested_delimiter="__")

    SQL_DB: SqlDBConfigurations
    VECTOR_DB: VectorDBConfigurations
    DROPBOX: DropboxConfigurations
    COHERE_API_KEY: str


configuration: Configuration = Configuration()
