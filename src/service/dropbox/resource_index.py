"""File index service module."""

import asyncio

from pydantic import InstanceOf, validate_call
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tokenizers import Tokenizer

from src.core import NotFoundError
from src.models.indexed_resource import IndexedResource
from src.schemas.dropbox import DropboxFileMetadata, ResourceType

from ..parser import Parser, ParserFactory
from ..utils import get_user_id_from_teams_id
from .service import DropboxService


class ResourceIndexService(DropboxService):
    """File index operations.

    This class is responsible for indexing the files of the Dropbox API.

    Methods:
        index_resource: Index the resource of a user.
    """

    tokenizer: InstanceOf[Tokenizer] = Tokenizer.from_pretrained(
        "Cohere/Cohere-embed-multilingual-v3.0"
    )

    @validate_call
    async def index_resource(
        self,
        user_teams_id: str,
        session: InstanceOf[AsyncSession],
        resource_id: str,
    ) -> None:
        """Index resource of a user.

        Arguments:
            user_teams_id: The teams id of the user.
            session: Database session.
            resource_id: The ID of the resource.

        Returns:
            None.

        Raises:
            NotFoundError: If the resources to index is not found.
        """
        user_id: int = await get_user_id_from_teams_id(
            teams_id=user_teams_id, session=session
        )
        access_token: str = await self._get_access_token(
            user_id=user_id, session=session
        )

        metadata: DropboxFileMetadata = (
            await self.dropbox_handler.get_metadata_of_resource(
                access_token=access_token, path=resource_id
            )
        )

        resources: list[DropboxFileMetadata] = []

        if metadata.type == ResourceType.FILE:
            resources.append(metadata)
        else:
            all_resources_from_api: list[
                DropboxFileMetadata
            ] = await self.dropbox_handler.get_all_resources(
                access_token=access_token, path=resource_id, recursive=True
            )
            for resource in all_resources_from_api:
                if resource.type == ResourceType.FILE:
                    resources.append(resource)

        if not resources:
            raise NotFoundError("Resources to index")

        await asyncio.gather(
            *[
                self._index_file(
                    user_id=user_id,
                    access_token=access_token,
                    resource=resource,
                    session=session,
                )
                for resource in resources
            ],
            return_exceptions=True,
        )

    @validate_call
    async def _index_file(
        self,
        user_id: int,
        access_token: str,
        resource: DropboxFileMetadata,
        session: InstanceOf[AsyncSession],
    ) -> None:
        """Index a file for a user.

        Arguments:
            user_id: The ID of the user.
            access_token: The access token of the user.
            resource: The resource metadata.
            session: Database session.

        Returns:
            None.

        Raises:
            NotFoundError: If the resource is not found.
            ValueError: If the file type is not supported.
        """
        indexed_resource = (
            await session.execute(
                select(IndexedResource)
                .filter(IndexedResource.user_id == user_id)
                .filter(IndexedResource.resource_id == resource.id)
            )
        ).fetchone()

        if indexed_resource:
            return

        content: str = await self._fetch_and_parse_content(
            access_token=access_token, resource=resource
        )

        chunks: list[str] = self.chunk_text_with_overlap(text=content)

        self.vector_db.batch_insert_objects(
            collection_name=f"user_{user_id}",
            chunks=chunks,
            resource=resource,
        )

        session.add(
            IndexedResource(  # type: ignore
                user_id=user_id,
                resource_id=resource.id,
            )
        )

    @validate_call
    async def _fetch_and_parse_content(
        self, access_token: str, resource: DropboxFileMetadata
    ) -> str:
        """Fetch and parse the content of a file.

        Arguments:
            access_token: The access token of the user.
            resource: The resource metadata.

        Returns:
            The content of the file.

        Raises:
            ValueError: If the file type is not supported.
        """
        content: bytes = await self.dropbox_handler.fetch_pdf_file_content(
            access_token=access_token, path=resource.id
        )
        file_extension: str = resource.name.split(".")[-1]
        try:
            parser: Parser = ParserFactory.create_parser(file_extension)
            return parser.parse(content)
        except ValueError as error:
            raise ValueError(f"Unsupported file type: {file_extension}") from error

    @validate_call
    def chunk_text_with_overlap(
        self, text: str, max_tokens: int = 256, overlap: int = 50
    ) -> list[str]:
        """Chunk the text with overlap.

        How to improve:
            Can be indexed by sentence while calculating token
                so there won't be any half sentence.

        Arguments:
            text: The text to chunk.
            max_tokens: The maximum number of tokens in a chunk.
            overlap: The number of overlapping tokens between chunks.

        Returns:
            The list of chunks.
        """
        tokens = self.tokenizer.encode(text).ids
        chunks: list[str] = []
        i: int = 0
        while i < len(tokens):
            chunk_tokens = tokens[i : i + max_tokens]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)
            i += max_tokens - overlap
        return chunks
