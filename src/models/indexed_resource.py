"""Model to store user's indexed resources."""

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from .mixin import IDMixin, TimestampMixin, text


class IndexedResource(Base, IDMixin, TimestampMixin):
    """Indexed resource model."""

    __tablename__ = "indexed_resource"

    resource_id: Mapped[text]
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False, index=True
    )
