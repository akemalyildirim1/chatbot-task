"""Unit tests for dropbox resource service."""

from datetime import datetime, timezone
import pytest


from service.utils import HttpResponse
from src.core import NotFoundError, InvalidInputError
from src.schemas.dropbox import DropboxAuthToken
from src.service.dropbox_resource import DropboxResourceService


@pytest.fixture
def dropbox_resource_service():
    return DropboxResourceService()


class TestGetTokensOfUserFromDB:
    async def test_ok(self, dropbox_resource_service, db_session):
        tokens = await dropbox_resource_service._get_tokens_of_user_from_db(
            user_id=1, session=db_session
        )
        assert isinstance(tokens, DropboxAuthToken)
        assert tokens.access_token == "test-access-token-1"
        assert tokens.refresh_token == "test-refresh-token-1"

    async def test_should_raise_not_found_error(
        self, dropbox_resource_service, db_session
    ):
        with pytest.raises(NotFoundError):
            await dropbox_resource_service._get_tokens_of_user_from_db(
                user_id=100, session=db_session
            )


class TestGenerateAccessTokenFromRefreshToken:
    async def test_ok(self, mocker, dropbox_resource_service):
        mocker.patch(
            "src.service.dropbox_resource.send_http_request",
            return_value=HttpResponse(
                data={
                    "access_token": "access-token",
                    "expires_in": 144000,
                },
                status=200,
                ok=True,
            ),
        )
        result = (
            await dropbox_resource_service._generate_access_token_from_refresh_token(
                refresh_token="refresh-token"
            )
        )
        assert isinstance(result, DropboxAuthToken)
        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"
        assert (
            result.expires_at - datetime.now(tz=timezone.utc)
        ).total_seconds() < 144000

    async def test_should_raise_invalid_input_error(
        self, mocker, dropbox_resource_service
    ):
        mocker.patch(
            "src.service.dropbox_login.send_http_request",
            return_value=HttpResponse(
                data={"error": "invalid_grant"},
                status=400,
                ok=False,
            ),
        )
        with pytest.raises(InvalidInputError) as error:
            await dropbox_resource_service._generate_access_token_from_refresh_token(
                refresh_token="invalid-token"
            )

        assert str(error.value) == "Invalid Refresh Token!"
