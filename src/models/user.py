"""User model."""

from sqlalchemy import TEXT
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixin import (
    IDMixin,
    TimestampMixin,
    text,
)


class User(Base, IDMixin, TimestampMixin):
    """User model."""

    __tablename__ = "users"

    teams_id: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False, index=True)
    name: Mapped[text]
