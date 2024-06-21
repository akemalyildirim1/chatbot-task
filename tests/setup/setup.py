"""Test data setup."""

from datetime import datetime, timezone, timedelta
import asyncio

from sqlalchemy import insert, text

from src.database import database_session_manager
from src.models import User, DropboxToken


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

        await session.execute(
            insert(DropboxToken),
            [
                {
                    "user_id": 1,
                    "access_token": "test-access-token-1",
                    "refresh_token": "test-refresh-token-1",
                    "expires_at": datetime.now(tz=timezone.utc) + timedelta(days=1),
                },
            ],
        )

        await session.execute(text("select setval('users_id_seq', 1000);"))


if __name__ == "__main__":
    print("Test data setup.")
    asyncio.run(setup())
    print("Test data setup completed.")
