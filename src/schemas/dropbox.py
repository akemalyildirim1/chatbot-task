"""Dropbox models module."""

from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class ResourceType(str, Enum):
    """Resource type enumeration."""

    FILE = "file"
    FOLDER = "folder"


class DropboxAuthToken(BaseModel):
    """Dropbox auth token model.

    Attributes:
        access_token: The access token.
        refresh_token: The refresh token.
        expires_at: The expiration time of the token.
    """

    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    expires_at: AwareDatetime


class DropboxFileMetadata(BaseModel):
    """Dropbox file metadata model."""

    id: str
    name: str
    type: ResourceType
    rev: str | None = Field(default=None)
    content_hash: str | None = Field(default=None)
    size: int | None = Field(default=None)
    path: str | None = Field(default=None)
    client_modified: AwareDatetime | None = Field(default=None)
    server_modified: AwareDatetime | None = Field(default=None)
