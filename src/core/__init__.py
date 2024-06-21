"""Module to store core configurations and settings."""

from .config import configuration
from .exceptions import (
    ConflictError,
    InvalidInputError,
    NotFoundError,
    UnprocessableEntityError,
)

__all__ = [
    "configuration",
    # Exceptions
    "ConflictError",
    "InvalidInputError",
    "NotFoundError",
    "UnprocessableEntityError",
]
