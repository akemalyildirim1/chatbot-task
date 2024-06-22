"""Dropbox login operations service."""

from pydantic import InstanceOf, validate_call
from service.utils import (
    add_tokens_to_db,
    get_user_id_from_teams_id,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import configuration
from src.schemas.dropbox import DropboxAuthToken

from .service import DropboxService


class DropboxLoginService(DropboxService):
    """Dropbox login operations.

    This service is responsible for the Dropbox login operations.

    Methods:
        generate_authorization_url: Generate the authorization URL.
        generate_tokens_from_code: Generate the access and refresh tokens
            from the code of the user.
    """

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
            "https://www.dropbox.com/oauth2/authorize?"
            f"response_type=code&client_id={configuration.DROPBOX.CLIENT_ID}&"
            f"redirect_uri={configuration.DROPBOX.REDIRECT_URI}&state={user_teams_id}&"
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
        tokens: DropboxAuthToken = (
            await self.dropbox_handler.get_access_and_refresh_token(code=code)
        )
        user_id: int = await get_user_id_from_teams_id(
            teams_id=user_teams_id, session=session
        )
        await add_tokens_to_db(user_id=user_id, tokens=tokens, session=session)
        return tokens
