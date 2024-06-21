"""Test data delete."""

import asyncio

from sqlalchemy import delete

from src.database import database_session_manager
from src.models import User, DropboxToken


async def teardown():
    """Delete test data."""
    async with database_session_manager.get_session() as session:
        await session.execute(delete(DropboxToken).filter(DropboxToken.user_id == 1))
        await session.execute(delete(User).filter(User.id.in_([1, 2, 3])))


if __name__ == "__main__":
    print("Deleting test data.")
    asyncio.run(teardown())
    print("Done.")
