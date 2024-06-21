"""Model to store user's dropbox tokens."""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixin import IDMixin, TimestampMixin, text


class DropboxToken(Base, IDMixin, TimestampMixin):
    """Dropbox token model."""

    __tablename__ = "dropbox_tokens"

    access_token: Mapped[text]
    refresh_token: Mapped[text]
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True, unique=True
    )
