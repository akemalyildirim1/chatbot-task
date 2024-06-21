"""Test fixtures."""

from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from .database import session_manager


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_manager.get_session() as session:
        yield session


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as client:
        yield client
