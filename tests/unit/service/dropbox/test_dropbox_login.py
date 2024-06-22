"""Unit tests for dropbox service."""

import pytest

from src.service.dropbox.login import DropboxLoginService


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
