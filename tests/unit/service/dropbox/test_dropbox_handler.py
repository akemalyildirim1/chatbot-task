"""Unit tests for dropbox handler."""

from datetime import datetime, timezone

import pytest

from src.core import InvalidInputError
from src.schemas.dropbox import DropboxAuthToken
from src.service.utils import HttpResponse
from src.service.dropbox.handler import DropboxHandler


@pytest.fixture
def dropbox_handler():
    return DropboxHandler()


class TestGenerateAccessTokenFromRefreshToken:
    async def test_ok(self, mocker, dropbox_handler):
        mocker.patch(
            "src.service.dropbox.handler.send_http_request",
            return_value=HttpResponse(
                data={
                    "access_token": "access-token",
                    "expires_in": 144000,
                },
                status=200,
                ok=True,
            ),
        )
        result = await dropbox_handler.generate_access_token_from_refresh_token(
            refresh_token="refresh-token"
        )
        assert isinstance(result, DropboxAuthToken)
        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"
        assert (
            result.expires_at - datetime.now(tz=timezone.utc)
        ).total_seconds() < 144000

    async def test_should_raise_invalid_input_error(self, mocker, dropbox_handler):
        mocker.patch(
            "src.service.dropbox.handler.send_http_request",
            return_value=HttpResponse(
                data={"error": "invalid_grant"},
                status=400,
                ok=False,
            ),
        )
        with pytest.raises(InvalidInputError) as error:
            await dropbox_handler.generate_access_token_from_refresh_token(
                refresh_token="invalid-token"
            )

        assert str(error.value) == "Invalid Refresh Token!"


class TestGetAccessAndRefreshToken:
    async def test_ok(self, mocker, dropbox_handler):
        mocker.patch(
            "src.service.dropbox.handler.send_http_request",
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
        result = await dropbox_handler.get_access_and_refresh_token(code="code")
        assert isinstance(result, DropboxAuthToken)
        assert result.access_token == "access-token"
        assert result.refresh_token == "refresh-token"
        assert (
            result.expires_at - datetime.now(tz=timezone.utc)
        ).total_seconds() < 144000

    async def test_should_raise_invalid_input_error(self, mocker, dropbox_handler):
        mocker.patch(
            "src.service.dropbox.handler.send_http_request",
            return_value=HttpResponse(
                data={"error": "invalid_grant"},
                status=400,
                ok=False,
            ),
        )
        with pytest.raises(InvalidInputError) as error:
            await dropbox_handler.get_access_and_refresh_token(code="invalid-code")

        assert str(error.value) == "Invalid Code!"
