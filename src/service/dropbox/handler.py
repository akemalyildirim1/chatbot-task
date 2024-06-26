"""Dropbox handler service module."""

from datetime import datetime, timedelta, timezone
from json import dumps
from typing import Any, Final

from aiohttp import ClientSession
from pydantic import BaseModel, validate_call

from src.core import InvalidInputError, configuration
from src.schemas.dropbox import DropboxAuthToken, DropboxFileMetadata, ResourceType
from src.service.utils import HttpResponse, send_http_request


class DropboxHandler(BaseModel):
    """Dropbox handler operations.

    This class is responsible for handling the Dropbox API operations.

    Attributes:
        redirect_uri: The redirect URI.
        client_id: The client ID.
        client_secret: The client secret.

    Methods:
        get_access_and_refresh_token: Get access and refresh token
            from the code of the user.
        generate_access_token_from_refresh_token: Generate an access token
            from a refresh token.
        get_metadata_of_resource: Get metadata of the given resource.
        get_all_resources: Get all resources of the given path.
        fetch_pdf_file_content: Fetch the content of the PDF file.
    """

    redirect_uri: Final[str] = configuration.DROPBOX.REDIRECT_URI
    client_id: Final[str] = configuration.DROPBOX.CLIENT_ID
    client_secret: Final[str] = configuration.DROPBOX.CLIENT_SECRET

    @validate_call
    async def get_access_and_refresh_token(self, code: str) -> DropboxAuthToken:
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

    @validate_call
    async def generate_access_token_from_refresh_token(
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
    async def get_metadata_of_resource(
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

    @validate_call
    async def get_all_resources(
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
    async def fetch_pdf_file_content(self, access_token: str, path: str) -> bytes:
        """Fetch the content of the PDF file.

        Arguments:
            access_token: The access token.
            path: The path of the file.

        Returns:
            The content of the PDF file.

        Raises:
            InvalidInputError: If the file is not found.
        """
        headers_download = {
            "Authorization": f"Bearer {access_token}",
            "Dropbox-API-Arg": f'{{"path": "{path}"}}',
        }

        async with ClientSession() as session, session.post(
            "https://content.dropboxapi.com/2/files/download",
            headers=headers_download,
        ) as response:
            if not response.ok:
                raise InvalidInputError("File")
            content = await response.read()
            return content
