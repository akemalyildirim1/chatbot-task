"""Unit tests for dropbox service."""

import pytest

from src.core import NotFoundError
from src.schemas.dropbox import DropboxAuthToken
from src.service.dropbox.service import DropboxService


@pytest.fixture
def dropbox_service():
    return DropboxService()


class TestGetTokensOfUserFromDB:
    async def test_ok(self, dropbox_service, db_session):
        tokens = await dropbox_service._get_tokens_of_user_from_db(
            user_id=1, session=db_session
        )
        assert isinstance(tokens, DropboxAuthToken)
        assert tokens.access_token == "test-access-token-1"
        assert tokens.refresh_token == "test-refresh-token-1"

    async def test_should_raise_not_found_error(self, dropbox_service, db_session):
        with pytest.raises(NotFoundError):
            await dropbox_service._get_tokens_of_user_from_db(
                user_id=100, session=db_session
            )
