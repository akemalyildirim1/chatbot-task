"""Shared service module for other services."""

from pydantic import BaseModel


class Service(BaseModel):
    """Service class for the application."""
