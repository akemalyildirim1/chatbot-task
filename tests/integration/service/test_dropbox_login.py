"""Integration tests for dropbox service."""

import pytest

from src.schemas.dropbox import DropboxAuthToken
from src.service.dropbox_login import DropboxLoginService

from tests.unit.service.test_dropbox_login import dropbox_login_service


_ = dropbox_login_service


@pytest.fixture
async def mock_get_access_and_refresh_token(mocker):
    async def _get_access_and_refresh_token(*args, **kwargs):
        return DropboxAuthToken(
            access_token="access_token", refresh_token="refresh_token"
        )

    return mocker.patch.object(
        DropboxLoginService,
        "_get_access_and_refresh_token",
        side_effect=_get_access_and_refresh_token,
    )


@pytest.fixture
async def mock_add_tokens_to_db(mocker):
    async def _add_tokens_to_db(*args, **kwargs):
        return None

    return mocker.patch.object(
        DropboxLoginService,
        "_add_tokens_to_db",
        side_effect=_add_tokens_to_db,
    )


@pytest.fixture
async def mock_get_user_id_from_teams_id(mocker):
    return mocker.patch(
        "src.service.dropbox_login.get_user_id_from_teams_id", return_value=1234
    )


class TestGenerateTokensFromCode:
    async def test_ok(
        self,
        dropbox_login_service,
        db_session,
        mock_get_access_and_refresh_token,
        mock_get_user_id_from_teams_id,
        mock_add_tokens_to_db,
    ):
        await dropbox_login_service.generate_tokens_from_code(
            code="code", user_teams_id="user_teams_id", session=db_session
        )
        mock_get_access_and_refresh_token.assert_called_once_with(code="code")
        mock_get_user_id_from_teams_id.assert_called_once_with(
            teams_id="user_teams_id", session=db_session
        )
        mock_add_tokens_to_db.assert_called_once_with(
            user_id=1234,
            tokens=DropboxAuthToken(
                access_token="access_token",
                refresh_token="refresh_token",
            ),
            session=db_session,
        )
