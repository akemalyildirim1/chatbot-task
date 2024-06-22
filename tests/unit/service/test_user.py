"""Unit tests for user service."""

import pytest
from sqlalchemy import select

from database import VectorDB
from src.core.exceptions import ConflictError
from src.models.user import User
from src.schemas.user import UserCreateSchema
from src.service.user import UserService

from tests import mock_async_func_generator


# VectorDB and MockVectorDB should be implemented from
# abc. They shouldn't depend on each other ideally.
class MockVectorDB(VectorDB):
    def create_collection(self, collection_name: str) -> None:
        pass


@pytest.fixture
def user_service():
    return UserService(vector_db=MockVectorDB())


class TestCreateUser:
    async def test_should_insert_ok(self, user_service, db_session):
        await user_service.create_user(
            session=db_session,
            user=UserCreateSchema(
                teams_id="random-uuid",
                name="New user",
            ),
        )

        [user_in_db] = (
            await db_session.execute(
                select(User).filter(User.teams_id == "random-uuid")
            )
        ).fetchone()

        assert user_in_db.name == "New user"
        assert user_in_db.teams_id == "random-uuid"
        assert user_in_db.id is not None

    async def test_should_raise_conflict_error(self, user_service, db_session):
        with pytest.raises(ConflictError) as error:
            await user_service.create_user(
                session=db_session,
                user=UserCreateSchema(
                    teams_id="test-user-1",
                    name="Other user name",
                ),
            )

        assert str(error.value) == "User already exists!"
