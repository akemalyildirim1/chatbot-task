"""Base model for SQLAlchemy models."""

from models.mixin import IDMixin, TimestampMixin
from sqlalchemy.orm import as_declarative


@as_declarative()
class Base(IDMixin, TimestampMixin):
    """Base class for all SQLAlchemy models."""
