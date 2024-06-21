"""Module to store core configurations and settings."""

from .config import configuration
from .exceptions import ConflictError, NotFoundError

__all__ = [
    "configuration",
    # Exceptions
    "ConflictError",
    "NotFoundError",
]
