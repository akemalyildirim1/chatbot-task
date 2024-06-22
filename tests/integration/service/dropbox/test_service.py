"""Integration tests for dropbox services."""

from datetime import datetime, timezone, timedelta

from src.schemas.dropbox import DropboxAuthToken

from tests import mock_async_func_generator
from tests.unit.service.dropbox.test_service import dropbox_service

_ = dropbox_service


class TestGetAccessToken:
    async def test_ok(
        self,
        mocker,
        dropbox_service,
        db_session,
    ):
        mocker.patch.object(
            dropbox_service,
            "_get_tokens_of_user_from_db",
            side_effect=mock_async_func_generator(
                DropboxAuthToken(
                    access_token="access-token",
                    refresh_token="refresh-token",
                    expires_at=datetime.now(tz=timezone.utc) + timedelta(days=1),
                )
            ),
        )

        result = await dropbox_service._get_access_token(
            user_id=1234, session=db_session
        )
        assert isinstance(result, str)
        assert result == "access-token"
