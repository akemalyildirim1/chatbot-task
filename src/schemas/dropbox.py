"""Dropbox models module."""

from pydantic import BaseModel


class DropboxAuthToken(BaseModel):
    """Dropbox auth token model.

    Attributes:
        access_token: The access token.
        refresh_token: The refresh token.
    """

    access_token: str
    refresh_token: str
