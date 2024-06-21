"""Unit tests for util functions."""

from datetime import datetime, timezone

import pytest

from sqlalchemy import select

from src.schemas.dropbox import DropboxAuthToken
from src.core import NotFoundError
from src.models import DropboxToken
from src.service.utils import get_user_id_from_teams_id, add_tokens_to_db


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


class TestAddTokensToDB:
    tokens = DropboxAuthToken(
        access_token="access-token",
        refresh_token="refresh-token",
        expires_at=datetime(2024, 1, 3, 12, tzinfo=timezone.utc),
    )

    @pytest.mark.parametrize("user_id", [1, 3])
    async def test_should_override_and_insert(self, db_session, user_id):
        """
        For user 1 -> Override
        For user 3 -> Insert
        """
        await add_tokens_to_db(
            user_id=user_id,
            tokens=self.tokens,
            session=db_session,
        )

        [token_in_db] = (
            await db_session.execute(
                select(DropboxToken).filter(DropboxToken.user_id == user_id)
            )
        ).fetchone()
        assert token_in_db.access_token == "access-token"
        assert token_in_db.refresh_token == "refresh-token"
        assert token_in_db.expires_at == datetime(2024, 1, 3, 12, tzinfo=timezone.utc)

    async def test_should_raise_not_found_error(self, db_session):
        with pytest.raises(NotFoundError) as error:
            await add_tokens_to_db(
                user_id=999,
                tokens=self.tokens,
                session=db_session,
            )

        assert str(error.value) == "User not found!"
