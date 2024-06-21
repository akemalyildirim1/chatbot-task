"""Test data setup."""

import asyncio

from sqlalchemy import insert

from src.database import database_session_manager
from src.models import User


async def setup():
    """Setup test data."""
    async with database_session_manager.get_session() as session:
        await session.execute(
            insert(User),
            [
                {
                    "id": 1,
                    "teams_id": "test-user-1",
                    "name": "Test One",
                },
                {
                    "id": 2,
                    "teams_id": "test-user-2",
                    "name": "Test Two",
                },
                {
                    "id": 3,
                    "teams_id": "test-user-3",
                    "name": "Test Three",
                },
            ],
        )


if __name__ == "__main__":
    print("Test data setup.")
    asyncio.run(setup())
    print("Test data setup completed.")
