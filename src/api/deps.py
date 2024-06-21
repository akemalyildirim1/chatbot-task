"""Shared dependencies for HTTP api."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import database_session_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    async with database_session_manager.get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
