"""Unit tests for dropbox service."""

import pytest

from sqlalchemy import select

from service.utils import HttpResponse
from src.core import NotFoundError, InvalidInputError
from src.models.dropbox_token import DropboxToken
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


class TestAddTokensToDB:
    tokens = DropboxAuthToken(
        access_token="access-token",
        refresh_token="refresh-token",
    )

    @pytest.mark.parametrize("user_id", [1, 3])
    async def test_should_override_and_insert(
        self, dropbox_login_service, db_session, user_id
    ):
        """
        For user 1 -> Override
        For user 3 -> Insert
        """
        await dropbox_login_service._add_tokens_to_db(
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

    async def test_should_raise_not_found_error(
        self, dropbox_login_service, db_session
    ):
        with pytest.raises(NotFoundError) as error:
            await dropbox_login_service._add_tokens_to_db(
                user_id=999,
                tokens=self.tokens,
                session=db_session,
            )

        assert str(error.value) == "User not found!"


class TestGetAccessAndRefreshToken:
    async def test_ok(self, mocker, dropbox_login_service):
        mock_send_request = mocker.patch(
            "src.service.dropbox_login.send_http_request",
            return_value=HttpResponse(
                data={
                    "access_token": "access-token",
                    "refresh_token": "refresh-token",
                },
                status=200,
                ok=True,
            ),
        )
        result = await dropbox_login_service._get_access_and_refresh_token(code="code")
        assert isinstance(result, DropboxAuthToken)
        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"

    async def test_should_raise_invalid_input_error(
        self, mocker, dropbox_login_service
    ):
        mock_send_request = mocker.patch(
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
