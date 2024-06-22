"""Shared dependencies for HTTP api."""

from typing import Annotated, AsyncGenerator

from fastapi import Depends, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import database_session_manager


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    async with database_session_manager.get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class UserTeamsIdDependency(BaseModel):
    """User teams id dependency."""

    teams_id: str = Field(
        Query(
            description="User's microsoft team id.",
        )
    )


class ResourcePathParams(BaseModel):
    """Path parameters for resource operations."""

    resource_id: str = Path(description="Resource ID.")
