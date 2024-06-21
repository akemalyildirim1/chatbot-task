"""Integration tests for dropbox resource service."""

from datetime import datetime, timezone, timedelta

import pytest

from src.schemas.dropbox import DropboxAuthToken
from src.service.dropbox_login import DropboxLoginService

from tests import mock_async_func_generator

from tests.unit.service.test_dropbox_resource import dropbox_resource_service

_ = dropbox_resource_service


class TestGetAccessToken:
    async def test_ok(
        self,
        mocker,
        dropbox_resource_service,
        db_session,
    ):
        mocker.patch.object(
            dropbox_resource_service,
            "_get_tokens_of_user_from_db",
            side_effect=mock_async_func_generator(
                DropboxAuthToken(
                    access_token="access-token",
                    refresh_token="refresh-token",
                    expires_at=datetime.now(tz=timezone.utc) + timedelta(days=1),
                )
            ),
        )

        result = await dropbox_resource_service.get_access_token(
            user_id=1234, session=db_session
        )
        assert isinstance(result, str)
        assert result == "access-token"

    async def test_should_generate_new_token(
        self, mocker, dropbox_resource_service, db_session
    ):
        mock_get_tokens = mocker.patch.object(
            dropbox_resource_service,
            "_get_tokens_of_user_from_db",
            side_effect=mock_async_func_generator(
                DropboxAuthToken(
                    access_token="access-token",
                    refresh_token="refresh-token",
                    expires_at=datetime.now(tz=timezone.utc),
                )
            ),
        )
        new_tokens = DropboxAuthToken(
            access_token="new-access-token",
            refresh_token="new-refresh-token",
            expires_at=datetime.now(tz=timezone.utc) + timedelta(days=1),
        )
        mock_generate_tokens = mocker.patch.object(
            dropbox_resource_service,
            "_generate_access_token_from_refresh_token",
            side_effect=mock_async_func_generator(new_tokens),
        )

        mock_add_tokens = mocker.patch(
            "src.service.dropbox_resource.add_tokens_to_db",
        )

        result = await dropbox_resource_service.get_access_token(
            user_id=1234, session=db_session
        )
        assert isinstance(result, str)
        assert result == "new-access-token"
        mock_get_tokens.assert_called_once_with(user_id=1234, session=db_session)
        mock_generate_tokens.assert_called_once_with(
            refresh_token="refresh-token",
        )
        mock_add_tokens.assert_called_once_with(
            user_id=1234,
            tokens=new_tokens,
            session=db_session,
        )
