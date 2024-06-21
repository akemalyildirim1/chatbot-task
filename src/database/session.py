"""Module to handle database session."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from src.core import configuration

from .base_session import BaseSessionManager


class DatabaseSessionManager(BaseSessionManager):
    """Database session manager.

    Methods:
        get_session: Get a new database session.
    """

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a database session for a transaction."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e from e
            finally:
                await session.close()


database_session_manager: DatabaseSessionManager = DatabaseSessionManager(
    str(configuration.SQL_DB.psql_url)
)
