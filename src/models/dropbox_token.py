"""Model to store user's dropbox tokens."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

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
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
