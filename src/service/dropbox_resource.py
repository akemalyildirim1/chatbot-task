"""Dropbox resource service module."""

from datetime import datetime, timedelta, timezone
from json import dumps
from typing import Any, Final

from pydantic import InstanceOf, validate_call
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import InvalidInputError, NotFoundError, configuration
from src.models.dropbox_token import DropboxToken
from src.schemas.dropbox import DropboxAuthToken, DropboxFileMetadata, ResourceType

from .service import Service
from .utils import (
    HttpResponse,
    add_tokens_to_db,
    get_user_id_from_teams_id,
    send_http_request,
)


class DropboxResourceService(Service):
    """Dropbox resource operations."""

    client_id: Final[str] = configuration.DROPBOX.CLIENT_ID
    client_secret: Final[str] = configuration.DROPBOX.CLIENT_SECRET

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
        return await self.get_access_token(user_id=user_id, session=session)

    @validate_call
    async def get_resources_of_given_resource(
        self, user_teams_id: str, session: InstanceOf[AsyncSession], path: str = ""
    ) -> list[DropboxFileMetadata]:
        """Get the resources and their metadata of the given path.

        Arguments:
            user_teams_id: The teams id of the user.
            session: Database session.
            path: Path to search for resources.

        Returns:
            The resources of the given path.

        Raises:
            InvalidInputError: If the path is invalid.
            NotFoundError: If the user is not found or
                tokens not found.
        """
        access_token: str = await self.get_access_token_from_teams_id(
            user_teams_id=user_teams_id, session=session
        )
        return await self._get_resources_from_api(
            access_token=access_token,
            path=path,
        )

    @validate_call
    async def get_children_resources(
        self, user_teams_id: str, session: InstanceOf[AsyncSession], resource_id: str
    ) -> list[str]:
        """Get the children resources of the given resource.

        Arguments:
            user_teams_id: The teams id of the user.
            session: Database session.
            resource_id: Resource ID.

        Returns:
            The children resources of the given resource.

        Raises:
            InvalidInputError: If the resource ID is invalid.
            NotFoundError: If the user is not found or
                tokens not found.
        """
        access_token: str = await self.get_access_token_from_teams_id(
            user_teams_id=user_teams_id, session=session
        )

        resources: list[DropboxFileMetadata] = await self._get_resources_from_api(
            access_token=access_token,
            path=resource_id,
        )
        return [r.id for r in resources]

    @validate_call
    async def get_metadata_of_resource(
        self, user_teams_id: str, session: InstanceOf[AsyncSession], resource_id: str
    ) -> DropboxFileMetadata:
        """Get the metadata of the given resource.

        Arguments:
            user_teams_id: The teams id of the user.
            session: Database session.
            resource_id: Resource ID.

        Returns:
            The metadata of the given resource.

        Raises:
            InvalidInputError: If the resource ID is invalid.
            NotFoundError: If the user is not found or
                tokens not found.
        """
        access_token: str = await self.get_access_token_from_teams_id(
            user_teams_id=user_teams_id, session=session
        )
        return await self._get_metadata_of_resource_from_api(
            access_token=access_token,
            path=resource_id,
        )

    @validate_call
    async def get_access_token(
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
            tokens = await self._generate_access_token_from_refresh_token(
                refresh_token=tokens.refresh_token
            )
            await add_tokens_to_db(user_id=user_id, tokens=tokens, session=session)

        return tokens.access_token

    @validate_call
    async def _get_resources_from_api(
        self,
        access_token: str,
        path: str = "",
        recursive: bool = False,
    ) -> list[DropboxFileMetadata]:
        """Get all resources of the given path from the Dropbox API.

        Arguments:
            access_token: The access token of user.
            path: Path to search for resources.
            recursive: Whether to search recursively.

        Returns:
            The resources of the given path.

        Raises:
            InvalidInputError: If the path is invalid.
        """
        result: HttpResponse = await send_http_request(
            "https://api.dropboxapi.com/2/files/list_folder",
            method="POST",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            body=dumps({"path": path, "recursive": recursive}),
        )

        if not result.ok:
            raise InvalidInputError("Resource")

        return [
            DropboxFileMetadata(
                id=r["id"],
                name=r["name"],
                type=ResourceType(r[".tag"]),
                rev=r.get("rev", None),
                path=r.get("path_lower", None),
                content_hash=r.get("content_hash", None),
                size=r.get("size", None),
            )
            for r in result.data["entries"]
        ]

    @validate_call
    async def _get_metadata_of_resource_from_api(
        self,
        access_token: str,
        path: str,
    ) -> DropboxFileMetadata:
        """Get metadata of the given resource from the Dropbox API.

        Arguments:
            access_token: The access token of user.
            path: Path to search for resources.

        Returns:
            The metadata of the given resource.

        Raises:
            InvalidInputError: If the path is invalid.
        """
        result: HttpResponse = await send_http_request(
            "https://api.dropboxapi.com/2/files/get_metadata",
            method="POST",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
            body=dumps({"path": path}),
        )

        if not result.ok:
            raise InvalidInputError("Resource")

        data: dict[str, Any] = result.data

        return DropboxFileMetadata(
            id=data["id"],
            name=data["name"],
            type=ResourceType(data[".tag"]),
            rev=data.get("rev"),
            path=data.get("path_lower"),
            content_hash=data.get("content_hash"),
            size=data.get("size"),
            client_modified=data.get("client_modified"),
            server_modified=data.get("server_modified"),
        )

    # Helpers.
    @validate_call
    async def _generate_access_token_from_refresh_token(
        self, refresh_token: str
    ) -> DropboxAuthToken:
        """Generate an access token from a refresh token.

        Arguments:
            refresh_token: The refresh token.

        Returns:
            The refreshed access token.

        Raises:
            InvalidInputError: If the refresh token is invalid.
        """
        response: HttpResponse = await send_http_request(
            url="https://api.dropboxapi.com/oauth2/token",
            method="POST",
            body={
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        if not response.ok:
            raise InvalidInputError("Refresh Token")

        return DropboxAuthToken(
            access_token=response.data["access_token"],
            refresh_token=refresh_token,
            expires_at=datetime.now(tz=timezone.utc)
            + timedelta(seconds=response.data["expires_in"]),
        )

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
