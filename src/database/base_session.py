"""Base class for database session."""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class BaseSessionManager(ABC):
    """Base class for database session manager."""

    def __init__(self, database_url: str):
        """Initialize the database session manager."""
        self.engine: AsyncEngine = create_async_engine(
            database_url, echo=True, pool_size=20, max_overflow=10, future=True
        )
        self.async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
        )

    @abstractmethod
    @asynccontextmanager
    def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a new database session."""
