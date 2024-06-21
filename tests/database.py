"""Test database."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.core import configuration
from src.database.base_session import BaseSessionManager


class TestDatabaseSessionManager(BaseSessionManager):
    """Test database session manager.

    Methods:
        get_session: Get a new database session.
    """

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a database session for a transaction."""
        async with self.async_session() as session:
            try:
                await self.engine.dispose()
                yield session
            except Exception as e:
                raise e from e
            finally:
                await session.rollback()
                await session.close()


session_manager: TestDatabaseSessionManager = TestDatabaseSessionManager(
    str(configuration.SQL_DB.psql_url)
)
