"""Vector Database operations service."""

from contextlib import contextmanager
from typing import Final, Generator

from pydantic import BaseModel, validate_call
from weaviate import WeaviateClient, connect_to_wcs
from weaviate.auth import AuthApiKey
from weaviate.classes import config as wvconfig

from src.core import configuration
from src.schemas.dropbox import DropboxFileMetadata
from src.schemas.query import Query


class VectorDB(BaseModel):
    """Vector Database operations.

    Attributes:
        api_key: The API key to connect to the vector database.
        host: The host of the vector database.
        cohere_key: The API key to connect to the Cohere API.
    """

    api_key: Final[str] = configuration.VECTOR_DB.KEY
    host: Final[str] = configuration.VECTOR_DB.HOST
    cohere_key: Final[str] = configuration.COHERE_API_KEY

    @contextmanager
    def connect(self) -> Generator[WeaviateClient, None, None]:
        """Connect to the vector database.

        Yields:
            The Weaviate client.
        """
        client: WeaviateClient = connect_to_wcs(
            cluster_url=self.host,
            auth_credentials=AuthApiKey(
                self.api_key,
            ),
            headers={
                "X-Cohere-Api-Key": self.cohere_key,
            },
        )
        try:
            yield client
        finally:
            client.close()

    @validate_call
    def create_collection(self, collection_name: str) -> None:
        """Create a collection in the vector database.

        Arguments:
            collection_name: The name of the collection.

        Returns:
            None.
        """
        with self.connect() as client:
            client.collections.create(
                name=collection_name,
                vectorizer_config=[
                    wvconfig.Configure.NamedVectors.text2vec_cohere(
                        name="content_vector",
                        source_properties=["content"],
                        vectorize_collection_name=False,
                    ),
                ],
                properties=[
                    wvconfig.Property(name="content", data_type=wvconfig.DataType.TEXT),
                    wvconfig.Property(
                        name="resource_id", data_type=wvconfig.DataType.TEXT
                    ),
                    wvconfig.Property(name="name", data_type=wvconfig.DataType.TEXT),
                    wvconfig.Property(name="path", data_type=wvconfig.DataType.TEXT),
                ],
            )

    @validate_call
    def batch_insert_objects(
        self, collection_name: str, chunks: list[str], resource: DropboxFileMetadata
    ) -> None:
        """Batch insert objects into the collection.

        Arguments:
            collection_name: The name of the collection.
            chunks: The objects to insert.
            resource: The resource metadata.

        Returns:
            None.
        """
        with self.connect() as client:
            collection = client.collections.get(
                name=collection_name,
            )
            with collection.batch.dynamic() as batch:
                for chunk in chunks:
                    batch.add_object(
                        properties={
                            "content": chunk,
                            "resource_id": resource.id,
                            "name": resource.name,
                            "path": resource.path,
                        },
                    )

    @validate_call
    def query(self, collection_name: str, query: str) -> dict[str, Query]:
        """Query the resources of a user.

        Arguments:
            collection_name: The name of the collection.
            query: The query to search.

        Returns:
            The result of the query as dictionary whose keys
                are resource ids.
        """
        with self.connect() as client:
            collection = client.collections.get(
                name=collection_name,
            )
            response = collection.query.near_text(
                query=query,
                # limit=2,
                distance=0.5,
            )

            result: dict[str, Query] = {}
            for obj in response.objects:
                property = obj.properties
                if property["resource_id"] not in result:
                    result[str(obj.properties["resource_id"])] = Query(
                        content=[],
                        name=str(property["name"]),
                        path=str(property["path"]),
                    )
                result[str(property["resource_id"])].content.append(
                    str(property["content"])
                )
            return result
