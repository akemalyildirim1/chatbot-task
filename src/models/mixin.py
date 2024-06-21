"""Common mixin and custom base classes."""

from datetime import datetime
from typing import Annotated

from sqlalchemy import BIGINT, REAL, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, declarative_mixin, declared_attr, mapped_column
from sqlalchemy.sql import func

# Types
serial_pk = Annotated[
    int,
    mapped_column(
        BIGINT,
        primary_key=True,
        autoincrement=True,
    ),
]
integer = Annotated[
    int,
    mapped_column(
        BIGINT,
        nullable=False,
    ),
]
real = Annotated[
    float,
    mapped_column(
        REAL,
        nullable=False,
    ),
]
boolean = Annotated[bool, mapped_column(Boolean, default=True, nullable=False)]
text = Annotated[str, mapped_column(String, nullable=False)]


class IDMixin:
    """Mixin for primary key."""

    id: Mapped[serial_pk]


class IsActiveMixin:
    """Mixin for is_active field."""

    is_active: Mapped[boolean]


class TimestampMixin:
    """Mixin for timestamp fields with timezone."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


@declarative_mixin
class TableNameMixin:
    """Mixin for table name."""

    @declared_attr
    def __tablename__(cls) -> str:
        """Generate table name."""
        return cls.__name__.lower()
