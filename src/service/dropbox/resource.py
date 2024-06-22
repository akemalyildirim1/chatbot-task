"""Dropbox resource service module."""

from aiohttp import ClientSession
from pydantic import InstanceOf, validate_call
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import InvalidInputError
from src.schemas.dropbox import DropboxFileMetadata

from .service import DropboxService


class DropboxResourceService(DropboxService):
    """Dropbox resource operations.

    This class is responsible for handling the resources of the Dropbox API.

    Methods:
        get_resources_of_given_resource: Get the resources and their
            metadata of the given path.
        get_children_resources: Get the children resources of the given resource.
        get_metadata_of_resource: Get the metadata of the given resource.
    """

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
        return await self.dropbox_handler.get_all_resources(
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

        resources: list[
            DropboxFileMetadata
        ] = await self.dropbox_handler.get_all_resources(
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
        return await self.dropbox_handler.get_metadata_of_resource(
            access_token=access_token,
            path=resource_id,
        )

    async def download_file(
        self, user_teams_id: str, session: InstanceOf[AsyncSession], resource_id: str
    ):
        """Download the file of the given resource.

        Arguments:
            user_teams_id: The teams id of the user.
            session: Database session.
            resource_id: Resource ID.

        Returns:
            The content of the file.

        Raises:
            InvalidInputError: If the resource ID is invalid.
            NotFoundError: If the user is not found or
                tokens not found.
        """
        access_token: str = await self.get_access_token_from_teams_id(
            user_teams_id=user_teams_id, session=session
        )
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Dropbox-API-Arg": f'{{"path": "{resource_id}"}}',
        }

        # Validate whether the resource ID is file or folder.
        async with ClientSession() as client_session, client_session.post(
            "https://content.dropboxapi.com/2/files/download",
            headers=headers,
        ) as resp_download:
            if resp_download.status != 200:
                raise InvalidInputError("Resource ID")
            async for chunk in resp_download.content.iter_any():
                yield chunk
