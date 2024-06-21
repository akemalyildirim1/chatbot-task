"""Dropbox operations service."""

from datetime import datetime, timedelta, timezone
from typing import Final

from pydantic import InstanceOf, validate_call
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import InvalidInputError, configuration
from src.schemas.dropbox import DropboxAuthToken

from .service import Service
from .utils import (
    HttpResponse,
    add_tokens_to_db,
    get_user_id_from_teams_id,
    send_http_request,
)


class DropboxLoginService(Service):
    """Dropbox login operations.

    This service is responsible for the Dropbox login operations.

    Methods:
        generate_authorization_url: Generate the authorization URL.
        generate_tokens_from_code: Generate the access and refresh tokens
            from the code of the user.
    """

    authorization_base_url: Final[str] = "https://www.dropbox.com/oauth2/authorize"

    redirect_uri: Final[str] = configuration.DROPBOX.REDIRECT_URI
    client_id: Final[str] = configuration.DROPBOX.CLIENT_ID
    client_secret: Final[str] = configuration.DROPBOX.CLIENT_SECRET

    @validate_call
    def generate_authorization_url(self, user_teams_id: str) -> str:
        """Generate the authorization URL.

        Arguments:
            user_teams_id: User's microsoft team id.

        Returns:
            The authorization URL.
        """
        # User id is passed as state to be used in the callback.
        return (
            f"{self.authorization_base_url}?"
            f"response_type=code&client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}&state={user_teams_id}&"
            f"token_access_type=offline"
        )

    @validate_call
    async def generate_tokens_from_code(
        self, code: str, user_teams_id: str, session: InstanceOf[AsyncSession]
    ) -> DropboxAuthToken:
        """Generate the access and refresh tokens from the code of the user.

        Arguments:
            code: The code to generate tokens.
            user_teams_id: User's microsoft team id.
            session: The database session.

        Returns:
            None.

        Raises:
            InvalidInputError: If the code is invalid.
            NotFoundError: If the user is not found.
        """
        tokens: DropboxAuthToken = await self._get_access_and_refresh_token(code=code)
        user_id: int = await get_user_id_from_teams_id(
            teams_id=user_teams_id, session=session
        )
        await add_tokens_to_db(user_id=user_id, tokens=tokens, session=session)
        return tokens

    # Helpers
    @validate_call
    async def _get_access_and_refresh_token(self, code: str) -> DropboxAuthToken:
        """Get access and refresh token from the code of the user.

        Arguments:
            code: The code to find tokens.

        Returns:
            The access and refresh tokens.

        Raises:
            InvalidInputError: If the code is invalid.
        """
        response: HttpResponse = await send_http_request(
            url="https://api.dropboxapi.com/oauth2/token",
            method="POST",
            body={
                "code": code,
                "grant_type": "authorization_code",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "redirect_uri": self.redirect_uri,
            },
        )
        if not response.ok:
            raise InvalidInputError("Code")

        return DropboxAuthToken(
            access_token=response.data["access_token"],
            refresh_token=response.data["refresh_token"],
            expires_at=datetime.now(tz=timezone.utc)
            + timedelta(seconds=response.data["expires_in"]),
        )
