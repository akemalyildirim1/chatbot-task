"""Unit tests for dropbox service."""

from datetime import datetime, timezone

import pytest


from service.utils import HttpResponse
from src.core import InvalidInputError
from src.schemas.dropbox import DropboxAuthToken
from src.service.dropbox_login import DropboxLoginService


@pytest.fixture
def dropbox_login_service():
    """Dropbox service fixture."""
    return DropboxLoginService()


class TestGenerateAuthorizationUrl:
    def test_ok(self, dropbox_login_service):
        result = dropbox_login_service.generate_authorization_url(
            user_teams_id="1234-5678"
        )
        assert isinstance(result, str)
        assert result == (
            "https://www.dropbox.com/oauth2/authorize?"
            "response_type=code&client_id=dropbox-client-id&"
            "redirect_uri=http://localhost:8000/dropbox/login/callback/"
            "&state=1234-5678&token_access_type=offline"
        )


class TestGetAccessAndRefreshToken:
    async def test_ok(self, mocker, dropbox_login_service):
        mocker.patch(
            "src.service.dropbox_login.send_http_request",
            return_value=HttpResponse(
                data={
                    "access_token": "access-token",
                    "refresh_token": "refresh-token",
                    "expires_in": 144000,
                },
                status=200,
                ok=True,
            ),
        )
        result = await dropbox_login_service._get_access_and_refresh_token(code="code")
        assert isinstance(result, DropboxAuthToken)
        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"
        assert (
            result.expires_at - datetime.now(tz=timezone.utc)
        ).total_seconds() < 144000

    async def test_should_raise_invalid_input_error(
        self, mocker, dropbox_login_service
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
            await dropbox_login_service._get_access_and_refresh_token(
                code="invalid-code"
            )

        assert str(error.value) == "Invalid Code!"
