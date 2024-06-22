"""Shared service module for other services."""

from database import VectorDB
from pydantic import BaseModel


class Service(BaseModel):
    """Service class for the application.

    Attributes:
        vector_db: The vector database operations.
    """

    vector_db: VectorDB = VectorDB()
