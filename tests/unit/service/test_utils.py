"""Unit tests for util functions."""

import pytest

from src.core import NotFoundError
from src.service.utils import get_user_id_from_teams_id


class TestGetUserIdFromTeamsID:
    async def test_ok(self, db_session):
        result = await get_user_id_from_teams_id(
            teams_id="test-user-1", session=db_session
        )
        assert isinstance(result, int)
        assert result == 1

    async def test_should_raise_not_found_error(self, db_session):
        with pytest.raises(NotFoundError) as error:
            await get_user_id_from_teams_id(
                teams_id="non-existing-user", session=db_session
            )
