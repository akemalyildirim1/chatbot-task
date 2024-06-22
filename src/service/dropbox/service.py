"""Dropbox common service."""

from datetime import datetime, timedelta, timezone

from pydantic import InstanceOf, validate_call
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import NotFoundError
from src.models.dropbox_token import DropboxToken
from src.schemas.dropbox import DropboxAuthToken
from src.service.service import Service
from src.service.utils import add_tokens_to_db, get_user_id_from_teams_id

from .handler import DropboxHandler


class DropboxService(Service):
    """Shared dropbox service.

    Attributes:
        dropbox_handler: Dropbox handler instance.

    Methods:
        get_access_token_from_teams_id: Get the access token of a
            user from the teams id.
    """

    dropbox_handler: DropboxHandler = DropboxHandler()

    @validate_call
    async def get_access_token_from_teams_id(
        self, user_teams_id: str, session: InstanceOf[AsyncSession]
    ) -> str:
        """Get the access token of a user from the teams id.

        Arguments:
            user_teams_id: The teams id of the user.
            session: Database session.

        Returns:
            The user's Dropbox access token.

        Raises:
            NotFoundError: If the user is not found or
                tokens not found.
        """
        user_id: int = await get_user_id_from_teams_id(
            teams_id=user_teams_id, session=session
        )
        return await self._get_access_token(user_id=user_id, session=session)

    @validate_call
    async def _get_access_token(
        self,
        user_id: int,
        session: InstanceOf[AsyncSession],
    ) -> str:
        """Get the access token of a user.

        Firstly, get the Dropbox tokens of the user. If the access token is
        expired,generate a new one from the refresh token.

        Arguments:
            user_id: User's ID.
            session: Database session.

        Returns:
            The user's Dropbox access token.

        Raises:
            NotFoundError: If the Dropbox tokens are not found.
        """
        tokens: DropboxAuthToken = await self._get_tokens_of_user_from_db(
            user_id=user_id, session=session
        )

        # 10 Minute buffer to avoid token expiration.
        if tokens.expires_at - datetime.now(tz=timezone.utc) < timedelta(minutes=5):
            tokens = (
                await self.dropbox_handler.generate_access_token_from_refresh_token(
                    refresh_token=tokens.refresh_token
                )
            )
            await add_tokens_to_db(user_id=user_id, tokens=tokens, session=session)

        return tokens.access_token

    @validate_call
    async def _get_tokens_of_user_from_db(
        self, user_id: int, session: InstanceOf[AsyncSession]
    ) -> DropboxAuthToken:
        """Get Dropbox tokens of a user.

        Arguments:
            user_id: User's ID.
            session: Database session.

        Returns:
            The user's Dropbox tokens.
        """
        tokens = (
            await session.execute(
                select(DropboxToken).filter(DropboxToken.user_id == user_id)
            )
        ).fetchone()

        if not tokens:
            raise NotFoundError("Dropbox tokens")

        return DropboxAuthToken.model_validate(tokens[0])
